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
    def lead(self, partners) -> "Build":
        """
        Build the first level of the {partners} along with mine, a run of tiles at a time, so
        the pages of the product each run needs are fetched once for all of us

        A partner qualifies when its first level has the layout of mine and, like mine, does
        not exist yet; the others build theirs on their own
        """
        # the layout of my first level
        mine = self.pyramid.layout(exponent=1)
        # whether it has to be built
        missing = not self.pyramid.holds(exponent=1)
        # go through the candidates
        for partner in partners:
            # the ones whose first level is laid out like mine and is missing like mine
            if (
                missing
                and partner.pyramid.layout(exponent=1) == mine
                and not partner.pyramid.holds(exponent=1)
            ):
                # follow me
                partner.leader = self
                # and join my pile
                self.partners.append(partner)
        # all done
        return self

    def start(self) -> "Build":
        """
        Hand out the first level that does not exist yet
        """
        # the pyramid
        pyramid = self.pyramid
        # how deep it goes
        self.depth = pyramid.depth()
        # a build whose first level is made by its leader waits for it
        if self.leader is not None:
            # which hands it the level when it starts
            return self
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
        onLevel=None,
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
        self.onLevel = onLevel
        self.onDone = onDone
        self.onFailed = onFailed
        # how many tiles travel in one task
        self.run = run
        # how many sample windows per axis the seed spreads over the extent
        self.windows = windows
        # the build that makes my first level along with its own, and the builds whose first
        # levels i make along with mine
        self.leader = None
        self.partners = []
        # the state of the level being built
        self.depth = 0
        self.exponent = 0
        self.occupancy = None
        self.runs = 0
        self.outstanding = set()
        # the pages the runs fetched from the product
        self.fetched = 0
        self.seeds = set()
        # whether the seed has reported, and whether the build is over
        self.seeded = False
        self.done = False
        self.error = None
        # all done
        return

    # implementation details
    def _receive(self, exponent: int, keys) -> None:
        """
        Get ready to take delivery of the level at {exponent}, whose runs, named by {keys}, my
        leader hands out along with its own
        """
        # the pyramid
        pyramid = self.pyramid
        # how deep it goes
        self.depth = pyramid.depth()
        # anything from an earlier run is on hand before more is measured
        pyramid.recall()
        # make the file, at its full padded size, before any worker can write into it
        pyramid.create(exponent=exponent)
        # the layout of the level
        _, _, grid = pyramid.layout(exponent=exponent)
        # the record of what gets written, nothing so far
        self.exponent = exponent
        self.occupancy = bytearray(grid[0] * grid[1])
        # the seed belongs to the leader
        self.seeds = set()
        # the runs, all of them outstanding
        self.outstanding = set(keys)
        self.runs = len(self.outstanding)
        # all done
        return

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
        # the runs: the seed tiles one at a time, and the rest in runs in raster order; a run no
        # longer than a row stays within its row, and a longer one carries on into the next,
        # so that a run as long as a band of rows is built by one worker, whose page buffer
        # keeps the pages the rows of the band share
        runs = [[seed] for seed in sorted(self.seeds)]
        # whether a run carries on past the end of a row
        wrap = self.run > grid[1]
        # the tiles of the current run
        stretch = []
        # go through the rows
        for row in range(grid[0]):
            # and the columns
            for col in range(grid[1]):
                # a seed is a run of its own
                if (row, col) in self.seeds:
                    # and is skipped here
                    continue
                # a run that is long enough is handed out as is
                if len(stretch) == self.run:
                    # add it to the pile
                    runs.append(stretch)
                    # and start a new one
                    stretch = []
                # add the tile to the current run
                stretch.append((row, col))
            # a run that stays within its row ends with it
            if not wrap and stretch:
                # add it to the pile
                runs.append(stretch)
                # and start over
                stretch = []
        # whatever is left is a run too
        if stretch:
            # add it to the pile
            runs.append(stretch)
        # the crew serves the newest task first, so the seeds go in last and come out
        # first; the bulk is reversed so the rows come out in order
        runs.reverse()
        # remember how many there are, so the progress of the level can be told
        self.runs = len(runs)
        # the partners, which only the first level has
        partners = self.partners if exponent == 1 else []
        # get them ready for the same runs
        for partner in partners:
            # by naming the runs
            partner._receive(exponent=exponent, keys=[tuple(tiles) for tiles in runs])
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
                partners=[partner.dataset for partner in partners],
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
            # a run of the first level was a run of my partners too
            if exponent == 1:
                # so theirs fail as well
                for partner in self.partners:
                    # unless they are over already
                    if not partner.done:
                        # say so
                        partner._fail(error=error)
            # and stop
            return
        # a run from a level other than the one being built is a bug
        if exponent != self.exponent:
            # make a channel
            channel = journal.firewall("qed.nexus.build")
            # complain
            channel.line(f"while building level {self.exponent} of '{self.dataset.pyre_name}'")
            channel.line(f"got records for level {exponent}")
            # flush
            channel.log()
            # and bail
            return
        # the width of the grid of tiles, for placing an entry in the record
        _, _, grid = self.pyramid.layout(exponent=exponent)
        # unpack the records of each raster of the run, and the pages it fetched to make them
        piles, fetched = result
        # count the pages
        self.fetched += fetched
        # mine come first
        result = piles[0]
        # the rest belong to my partners, in their order, on the first level
        if exponent == 1:
            # go through them
            for partner, pile in zip(self.partners, piles[1:]):
                # and hand each its own records; the pages are counted once, here
                partner._collect(exponent=exponent, key=key, result=([pile], 0))
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
        # the level exists now, which is worth telling whoever offers it to a client
        if self.onLevel is not None:
            # by calling the hook
            self.onLevel(build=self, exponent=exponent)
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

    def reach(self) -> int:
        """
        Report the deepest level available, counting from the first without gaps
        """
        # start below the first level
        reach = 0
        # and climb for as long as the next level exists
        while reach < self.depth and self.pyramid.holds(exponent=reach + 1):
            # one more
            reach += 1
        # all done
        return reach

    def describe(self) -> dict:
        """
        Describe the state of the build: the raster, how deep its pyramid goes and how deep it
        is available, and the level under construction with its runs and the ones still out
        """
        # the level under construction, while there is one
        level = self.exponent if self.exponent and not self.done else None
        # assemble the description
        return {
            "raster": self.dataset.pyre_name,
            "depth": self.depth,
            "reach": self.reach(),
            "level": level,
            "runs": self.runs if level is not None else 0,
            "outstanding": len(self.outstanding) if level is not None else 0,
            "fetched": self.fetched,
        }

    def _seeds(self) -> set:
        """
        The tiles of the first level that cover the windows the probe would have sampled
        """
        # the layout of the first level
        _, tile, _ = self.pyramid.layout(exponent=1)
        # the dataset's own windows, in its own coordinates
        origins = qed.readers.windows(dataset=self.dataset, stops=self.windows)
        # each one lands in the tile of the first level that holds its decimation
        return {(origin[0] // 2 // tile[0], origin[1] // 2 // tile[1]) for origin in origins}

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
        channel.line(f"could not build level {self.exponent} of '{self.dataset.pyre_name}'")
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
