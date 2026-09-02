# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import functools

# support
import journal
import qed

# the work that travels to the crew
from .Decimate import Decimate


# the server side record of a pyramid under construction
class Build:
    """
    The server side record of a pyramid under construction: what has been handed out, what
    has come back, and what that makes true

    The server owns everything the workers must not touch together: it makes the directory
    and pre-sizes every level before any tile is written, keeps the occupancy record from
    the tile records that come back, commits a level the moment its last run reports, and
    hands out the next level only then, since a worker can only read a level whose record
    exists. The statistics of the whole raster accumulate here too, from the records of the
    first level, so they are on hand long before the build is done.

    The first tiles handed out are the ones the probe would have sampled: a few tiles
    spread over the whole extent, whose records are enough of an estimate to render by.
    Once they have all reported the build is seeded, and the view stops waiting
    """

    # interface
    def start(self) -> "Build":
        """
        Hand out the first level that does not exist yet
        """
        # the pyramid
        pyramid = self.pyramid
        # how deep it goes
        self.depth = pyramid.depth()
        # look for the first missing level; the ones below it exist, since levels are
        # built in order and committed one at a time
        for exponent in range(1, self.depth + 1):
            # a level that exists needs nothing
            if pyramid.holds(exponent=exponent):
                # so move on
                continue
            # anything from an earlier run is on hand before more is measured
            pyramid.recall()
            # the first missing level is where the work starts
            self._dispatch(exponent=exponent)
            # all done
            return self
        # every level exists already, so the numbers an earlier run measured stand
        pyramid.recall()
        # there is nothing to wait for
        self._seeded()
        # and nothing to build
        self._finish()
        # all done
        return self

    # metamethods
    def __init__(
        self,
        reader,
        dataset,
        pyramid,
        fleet,
        statistics,
        onSeeded=None,
        onProgress=None,
        onDone=None,
        onFailed=None,
        run: int = 8,
        windows: int = 4,
        **kwds,
    ):
        # chain up
        super().__init__(**kwds)
        # the source and the dataset whose levels are being built
        self.reader = reader
        self.dataset = dataset
        # the pyramid, laid over a dataset this process never reads
        self.pyramid = pyramid
        # the crew the work goes to
        self.fleet = fleet
        # the accumulator the records of the first level fold into; it is shared with
        # whoever watches the numbers, and the pyramid writes it beside the levels
        self.statistics = statistics
        pyramid.statistics = statistics
        # the hooks
        self.onSeeded = onSeeded
        self.onProgress = onProgress
        self.onDone = onDone
        self.onFailed = onFailed
        # how many tiles travel in one task
        self.run = run
        # how many sample windows per axis the seed spreads over the extent
        self.windows = windows
        # the state of the level being built
        self.depth = 0
        self.exponent = 0
        self.occupancy = None
        self.outstanding = set()
        self.seeds = set()
        # whether the seed has reported, and whether the build is over
        self.seeded = False
        self.done = False
        self.error = None
        # all done
        return

    # implementation details
    def _dispatch(self, exponent: int) -> None:
        """
        Hand out every run of the level at {exponent}
        """
        # the pyramid
        pyramid = self.pyramid
        # make the file, at its full padded size, before any worker can write into it
        pyramid.create(exponent=exponent)
        # the layout of the level
        _, _, grid = pyramid.layout(exponent=exponent)
        # the record of what gets written, nothing so far
        self.exponent = exponent
        self.occupancy = bytearray(grid[0] * grid[1])
        # the tiles the seed samples, which only the first level has
        self.seeds = self._seeds() if exponent == 1 else set()
        # the runs: the seed tiles one at a time, and the rest in runs along each row
        runs = [[seed] for seed in sorted(self.seeds)]
        # go through the rows
        for row in range(grid[0]):
            # and the columns that are not seeds, in consecutive stretches
            stretch = []
            # by walking the row
            for col in range(grid[1] + 1):
                # a seed, or the end of the row, breaks a stretch
                if col == grid[1] or (row, col) in self.seeds:
                    # so whatever was accumulated is a run
                    if stretch:
                        # add it to the pile
                        runs.append(stretch)
                        # and start over
                        stretch = []
                    # move on
                    continue
                # a run that is long enough is handed out as is
                if len(stretch) == self.run:
                    # add it to the pile
                    runs.append(stretch)
                    # and start a new one
                    stretch = []
                # add the tile to the current run
                stretch.append((row, col))
        # the crew serves the newest task first, so the seeds go in last and come out
        # first; the bulk is reversed so the rows come out in order
        runs.reverse()
        # make a channel
        channel = journal.debug("qed.nexus.build")
        # show me
        channel.log(
            f"{self.dataset.pyre_name}: level {exponent} of {grid[0]}x{grid[1]} tiles "
            f"in {len(runs)} runs, {len(self.seeds)} of them seeds"
        )
        # go through the runs
        for tiles in runs:
            # the key of the run is its tiles
            key = tuple(tiles)
            # mark it as outstanding
            self.outstanding.add(key)
            # describe the work as a task that can travel to a worker
            task = Decimate(
                reader=self.reader,
                dataset=self.dataset,
                workspace=self.pyramid.workspace,
                exponent=exponent,
                tiles=tiles,
            )
            # and hand it to the crew
            self.fleet.decimate(
                task=task,
                callback=functools.partial(self._collect, exponent=exponent, key=key),
            )
        # all done
        return

    def _collect(self, exponent: int, key: tuple, result=None, error=None) -> None:
        """
        Take delivery of the records of one run of the level at {exponent}
        """
        # a build that is over ignores stragglers
        if self.done:
            # so do nothing
            return
        # a run that failed fails the build: the level cannot be committed without it
        if error is not None:
            # so say so
            self._fail(error=error)
            # and stop
            return
        # a run from a level other than the one being built is a bug
        if exponent != self.exponent:
            # make a channel
            channel = journal.firewall("qed.nexus.build")
            # complain
            channel.line(
                f"while building level {self.exponent} of '{self.dataset.pyre_name}'"
            )
            channel.line(f"got records for level {exponent}")
            # flush
            channel.log()
            # and bail
            return
        # the width of the grid of tiles, for placing an entry in the record
        _, _, grid = self.pyramid.layout(exponent=exponent)
        # go through the records
        for (row, col), record in result:
            # a tile that held anything was written
            if record[0]:
                # so name it in the record
                self.occupancy[row * grid[1] + col] = 1
            # the records of the first level describe the raster itself
            if exponent == 1:
                # so they fold into the statistics of the whole
                self.statistics.merge(record=record)
        # the run is in
        self.outstanding.discard(key)
        # let whoever watches the numbers know they moved
        if exponent == 1 and self.onProgress is not None:
            # by calling them
            self.onProgress(build=self)
        # the seed is in when none of its tiles is outstanding
        if not self.seeded and not any(
            len(run) == 1 and run[0] in self.seeds for run in self.outstanding
        ):
            # so the build is seeded
            self._seeded()
        # if runs are still out
        if self.outstanding:
            # wait for them
            return
        # otherwise the level is complete: commit its record, which makes it exist
        self.pyramid.commit(exponent=exponent, occupancy=self.occupancy)
        # the first level measured the raster; keep the numbers beside it
        if exponent == 1:
            # by writing the sidecar
            self.pyramid.remember()
        # the next level, if there is one
        following = exponent + 1
        # if there is
        if following <= self.depth:
            # hand it out
            self._dispatch(exponent=following)
            # and wait for it
            return
        # otherwise, the pyramid is done
        self._finish()
        # all done
        return

    def _seeds(self) -> set:
        """
        The tiles of the first level that cover the windows the probe would have sampled
        """
        # the layout of the first level
        _, tile, _ = self.pyramid.layout(exponent=1)
        # the dataset's own windows, in its own coordinates
        origins = qed.readers.windows(dataset=self.dataset, stops=self.windows)
        # each one lands in the tile of the first level that holds its decimation
        return {
            (origin[0] // 2 // tile[0], origin[1] // 2 // tile[1]) for origin in origins
        }

    def _seeded(self) -> None:
        """
        Mark the build as seeded, and let whoever is waiting know
        """
        # once
        if self.seeded:
            # is enough
            return
        # mark
        self.seeded = True
        # and notify
        if self.onSeeded is not None:
            # by calling the hook
            self.onSeeded(build=self)
        # all done
        return

    def _finish(self) -> None:
        """
        Mark the build as done, and let whoever is waiting know
        """
        # mark
        self.done = True
        # make a channel
        channel = journal.debug("qed.nexus.build")
        # show me
        channel.log(f"{self.dataset.pyre_name}: pyramid complete at depth {self.depth}")
        # and notify
        if self.onDone is not None:
            # by calling the hook
            self.onDone(build=self)
        # all done
        return

    def _fail(self, error) -> None:
        """
        Mark the build as failed, retaining {error} as the reason
        """
        # mark
        self.done = True
        self.error = error
        # make a channel
        channel = journal.warning("qed.nexus.build")
        # complain
        channel.line(
            f"could not build level {self.exponent} of '{self.dataset.pyre_name}'"
        )
        channel.line(f"got: {error}")
        # flush
        channel.log()
        # and notify
        if self.onFailed is not None:
            # by calling the hook
            self.onFailed(build=self, error=error)
        # all done
        return


# end of file
