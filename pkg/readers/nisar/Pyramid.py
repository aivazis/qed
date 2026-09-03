# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import hashlib
import json
import math
import os

# support
import journal
import pyre
import qed


# the decimated levels of a dataset, held beside the product they came from
class Pyramid:
    """
    The decimated levels of one dataset, stored in a cache beside the product

    A zoomed out view of a chunked product is expensive for a reason that has nothing to do
    with how many pixels it shows: a strided read touches every chunk its footprint covers,
    so at stride {s} the library decompresses {s}^2 cells for every cell the view keeps. The
    pyramid removes that cost by storing the decimated data, so a view at zoom {k} reads a
    small dataset at unit stride instead of a large one at stride {2^k}.

    Levels halve on each axis, which is what keeps a tile of a level exactly one chunk: any
    coarser factor would leave the intermediate zoom levels covering several chunks apiece,
    which is the very thing the pyramid exists to abolish. Because decimation is plain
    striding, and striding composes, level {k} is cell for cell what a stride of {2^k} over
    the base would have produced
    """

    # interface
    def level(self, zoom: tuple) -> tuple:
        """
        Report the source that serves a view at {zoom}, and the zoom still to apply to it

        {zoom} is a decimation exponent per axis, because the two axes are not required to
        agree: the client can decouple them, and a view zoomed out horizontally while held
        at full resolution vertically is an ordinary thing to ask for. My levels halve both
        axes together, so an asymmetric request is served by the deepest level that
        over-decimates neither axis -- which is the smaller of the two exponents -- and the
        difference is made up by striding what is read, per axis.

        A request always gets an answer: with no levels at all that is the base owing the
        whole decimation, which is exactly what the reader did before any of this existed.
        Fractional
        zoom never reaches here; the client asks for a whole level and scales the result
        itself
        """
        # the deepest level that would not over-decimate either axis
        wanted = min(zoom)
        # a request at or above full resolution on either axis is served by the base
        if wanted <= 0:
            # which still owes the whole decimation
            return self._base, tuple(zoom)
        # look for that level, then for progressively shallower ones
        for candidate in range(wanted, 0, -1):
            # if i hold this one
            if candidate in self._levels:
                # it serves the request, and each axis owes the difference. the origin of
                # the tile does not move: it is in decimated coordinates, and the render
                # scales it by whatever stride it is given, so the same origin lands on the
                # same cells whichever level supplies them
                return self._levels[candidate], tuple(
                    level - candidate for level in zoom
                )
        # nothing was built, so the base owes the whole decimation
        return self._base, tuple(zoom)

    def at(self, exponent: int):
        """
        Report the level decimated by exactly {exponent} halvings, or nothing when i do not
        hold one that deep

        This is the exact request, as opposed to {level}, which answers every zoom with the
        best it can do. A companion raster is asked this way, because a render that reads
        several rasters together must have all of them at one depth or none of them
        """
        # hand back what i hold, if anything
        return self._levels.get(exponent)

    def reach(self) -> int:
        """
        Report the depth of the deepest level i actually hold
        """
        # the levels are numbered by their depth, so the deepest is the largest
        return max(self._levels, default=0)

    def attach(self) -> "Pyramid":
        """
        Take hold of the levels an earlier pass built, without building any

        This is what a worker rendering a tile does: it reads what is there and renders off
        the product when there is nothing. A level is a mapped file, so many workers may
        hold the same level at once and none of them is in anybody's way. Attaching again
        later picks up the levels that have appeared since, which is how a worker learns
        that a build it did not take part in has reached deeper
        """
        # where my levels would be
        home = self.home
        # a workspace with nowhere to keep anything, or a product nobody has prepared
        if home is None or not home.exists():
            # has no levels to offer, and this must not be the thing that makes one
            return self
        # otherwise, take hold of what is there that i do not hold already
        self._survey()
        # and of what an earlier run measured while it built it
        self.recall()
        # all done
        return self

    def build(self, depth: int = 0) -> "Pyramid":
        """
        Make the levels up to {depth}, or as many as the extent supports

        Level 1 is the only one that reads the product; every level after it is built from
        the one above at a quarter the size, so the whole pyramid costs about a third more
        than the single pass that built its first level
        """
        # a dataset no kernel can read as it stands gets no levels at all
        if self._kernels is None or self._storage is None:
            # make a channel
            channel = journal.warning("qed.readers.pyramid")
            # explain, since the absence will show as a view that is slow rather than wrong
            channel.line(f"no levels built for '{self._name}'")
            channel.line(f"its cells are encoded, and only a decoder can read them")
            # flush
            channel.log()
            # and leave without building anything
            return self
        # where my levels live
        home = self.home
        # a workspace that could not make its cache has already complained
        if home is None:
            # so there is nothing to do
            return self
        # make my directory, if this is the first time
        home.mkdir(parents=True, exist_ok=True)
        # figure out how deep to go
        depth = depth if depth > 0 else self.depth()
        # take hold of whatever an earlier run left behind, so it is not built twice
        self.attach()
        # make a channel
        channel = journal.debug("qed.readers.pyramid")
        # go through the levels, shallowest first, since each one feeds the next
        for exponent in range(1, depth + 1):
            # if i already hold it
            if exponent in self._levels:
                # leave it alone; a level is immutable once written
                continue
            # the level it is built from
            source, _ = self.level(zoom=(exponent - 1, exponent - 1))
            # its extent, half the one below it on each axis
            extent = self._extent(exponent=exponent)
            # an extent that has collapsed cannot be halved again
            if min(extent) < 1:
                # so this is the top of the pyramid
                break
            # the tile the level is diced into
            tile = self._tileOf(extent=extent)
            # make the file at its full padded size and take hold of it for writing
            self.create(exponent=exponent)
            draft = self.draft(exponent=exponent)
            # the tiles of the level, in tile order; nothing is written yet
            _, _, grid = self.layout(exponent=exponent)
            occupancy = bytearray(math.prod(grid))
            # the width of the grid of tiles, for placing an entry in the record
            columns = grid[1]
            # walk it in tiles, which are chunks, so no chunk is written twice
            for origin, shape in self._tiles(extent=extent, tile=tile):
                # and fill each one by decimating the level below; a tile of pure fill is
                # skipped, so the level stays as sparse as the product it came from
                record = self._kernels.decimate(
                    source=source,
                    destination=draft,
                    datatype=self._datatype,
                    origin=origin,
                    shape=shape,
                    stride=(2, 2),
                )
                # the first level is the only one that reads the product, so it is the one
                # whose records describe the data rather than a decimation of it
                if exponent == 1:
                    # fold its measurement into the running statistics of the raster
                    self.statistics.merge(record=record)
                # a tile that held anything was written
                if record[0]:
                    # so name it in the record, at its place in tile order
                    occupancy[
                        (origin[0] // tile[0]) * columns + origin[1] // tile[1]
                    ] = 1
            # let go of the writable mapping; the level is complete
            del draft
            # commit the occupancy record, which is what makes the level exist
            self.commit(exponent=exponent, occupancy=occupancy)
            # and take hold of the level the way a reader would
            self._levels[exponent] = self._open(
                exponent=exponent, extent=extent, tile=tile
            )
            # show me
            channel.log(
                f"{self._name}: level {exponent} of extent {extent}, "
                f"{sum(occupancy)} tiles written"
            )
            # the statistics were measured while the first level was being built, and a
            # level is built once; keep them beside it, or a pyramid found on disk would
            # arrive without the very numbers it was the cheapest way to compute
            if exponent == 1:
                # so write them down
                self.remember()
        # all done
        return self

    def depth(self) -> int:
        """
        Report how many levels my extent supports

        Halving stops at the level that fits within a single tile: a client asking for a
        deeper zoom is served by striding that one tile, which is already the cheap case,
        so nothing above it would buy anything. A raster that fits in a tile to begin with
        gets no levels at all
        """
        # start at the base
        depth = 0
        # and the full extent
        extent = list(self._shape)
        # halve until the extent fits in a tile on both axes
        while any(axis > width for axis, width in zip(extent, self._tile)):
            # one more level
            depth += 1
            # and the extent shrinks
            extent = [axis // 2 for axis in extent]
        # all done
        return depth

    def close(self) -> "Pyramid":
        """
        Release my levels

        Each one is a mapping, and letting go of the last reference to it unmaps the file
        """
        # forget them
        self._levels = {}
        # all done
        return self

    # metamethods
    def __init__(self, reader, dataset, workspace, **kwds):
        # chain up
        super().__init__(**kwds)
        # remember what i am a pyramid of. the name has to be the dataset's identity within
        # its product, not the name this process happens to have given its reader: a crew
        # member calls the same reader something else, and a later run may call it a third
        # thing, and none of them could read a cache written under another's name
        self._path = self._designate(dataset=dataset)
        # and a readable spelling of it, for the diagnostics
        self._name = "/".join(self._path)
        self._shape = tuple(dataset.shape)
        self._tile = tuple(dataset.tile)
        self._datatype = dataset.datatype.htype
        # the payload, when there is one: a metadata-only twin on the team side has none,
        # and never serves a zoom; it lays out levels, hands out the work, and keeps the
        # records
        data = getattr(dataset, "data", None)
        self._base = data.dataset if data is not None else None
        # the kernels that read cells of this type. a raster whose samples are encoded
        # rather than stored has none, and it must not get levels: decimation is a read and
        # a write, and a read into a buffer laid out for the wrong cell type deposits
        # something that is not the data
        self._kernels = dataset.kernels
        # the storage classes for cells of this type, the level a reader maps and the draft
        # a builder writes, gathered under the same cell name as the kernels
        self._cell = dataset.datatype.cell
        self._storage = (
            getattr(qed.libqed.pyramid, self._cell, None) if self._cell else None
        )
        # what an unwritten chunk of a level must read back as. the decimation leaves a tile
        # unwritten exactly when it found no valid cell in it, and the only cell its kernels
        # call invalid is a nan -- so for a raster that can hold one, the fill is a nan and
        # nothing else, or a skipped chunk would come back holding a measurement the product
        # never made. this is not a free choice but the condition that makes a level
        # indistinguishable from the raster it was decimated from
        blank = dataset.cell.blank
        # the product's own declaration is deliberately not the authority here. on the
        # geocoded NISAR products it is actively wrong: they frame their data in nans while
        # declaring the library's default fill of zero, and a level built on that
        # declaration shows a black margin where the product shows nothing at all
        if blank is not None:
            # so the cell type decides
            self._fill = blank
        # a raster whose cells have no way to say "nothing" never has a tile skipped, since
        # every value it can hold is a measurement, so its fill is never read back and any
        # value will do
        else:
            # so zero stands
            self._fill = 0
        # the identity of the product this dataset came from, so a cache built against one
        # version of a file is never read against another
        self._stamp = self._identify(reader=reader, uri=dataset.uri)
        # where the cache lives is not mine to decide: the workspace the application owns
        # is the one authority on where derived data goes, and it is handed to me
        self._workspace = workspace
        # the levels i hold, by depth
        self._levels = {}
        # what the product turns out to hold; building the first level reads every cell of
        # it, so the statistics of the whole raster accumulate as a byproduct rather than
        # costing a pass of their own
        self.statistics = qed.ux.sample()
        # all done
        return

    # implementation details
    def _designate(self, dataset) -> tuple:
        """
        Build the path a dataset's levels live under, one step per coordinate
        """
        # its selector says which dataset of the product this is, in terms the product
        # itself supplies, so every process that opens the file agrees on the answer
        selector = dict(dataset.selector)
        # a product with no selector has one dataset, and needs no path to tell it apart
        if not selector:
            # so anything stable will do
            return ("data",)
        # otherwise, one group per coordinate, named by the coordinate itself, the way the
        # product names its own groups. the order is the selector's own, which the reader
        # builds in the order the product nests them -- band, then frequency, then the
        # polarization or covariance term -- so position says which axis a group belongs
        # to and the value need not repeat it. sorting the axes instead would be just as
        # deterministic and would scramble that into something alphabetical
        return tuple(str(value) for value in selector.values())

    def _identify(self, reader, uri) -> str:
        """
        Build the name that identifies the product this pyramid was derived from
        """
        # a product that carries an identifier for itself has already answered this
        # question, and answered it better than we could: a granule id is unique,
        # versioned, and means something to the people who produced the data
        granule = getattr(reader, "granule", None)
        # if there is one
        if granule:
            # it names the cache, with anything that cannot appear in a file name removed
            return "".join(c if c.isalnum() or c in "-_." else "_" for c in granule)
        # otherwise, fall back on the bytes: the address of the product
        address = str(getattr(uri, "address", uri))
        # attempt to
        try:
            # measure the file
            status = pyre.primitives.path(address).stat()
            # and record what would change if it were replaced
            mark = f"{address}:{status.st_size}:{status.st_mtime_ns}"
        # a product this process cannot stat, e.g. one on a remote store
        except OSError:
            # is identified by its address alone; a remote etag belongs here when the
            # archives can supply one
            mark = address
        # reduce it to something that can be a file name
        return hashlib.sha256(mark.encode("utf-8")).hexdigest()[:16]

    def _survey(self) -> dict:
        """
        Take hold of the levels my directory holds that i do not hold already
        """
        # go through the levels the extent could support
        for exponent in range(1, self.depth() + 1):
            # a level i already hold needs nothing
            if exponent in self._levels:
                # so skip it
                continue
            # a level without its record does not exist
            if not self.holds(exponent=exponent):
                # so neither does anything above it, since each level is built from the
                # one below; but keep looking, in case a stale record is all that is left
                continue
            # the extent of the level and its tile
            extent = self._extent(exponent=exponent)
            tile = self._tileOf(extent=extent)
            # carefully, since the files may not be what the record promises
            try:
                # take hold of it
                self._levels[exponent] = self._open(
                    exponent=exponent, extent=extent, tile=tile
                )
            # a file of the wrong size, or one that has gone missing, is refused
            except journal.ApplicationError as error:
                # make a channel
                channel = journal.warning("qed.readers.pyramid")
                # complain
                channel.line(f"could not attach level {exponent} of '{self._name}'")
                channel.line(f"at '{self.home}'")
                channel.line(f"got: {error}")
                # flush
                channel.log()
                # and move on without it
                continue
        # hand off the pile
        return self._levels

    def _open(self, exponent: int, extent: tuple, tile: tuple):
        """
        Map the level at {exponent} the way a reader does
        """
        # a level over cells of my type, with my fill standing in for whatever was not
        # written
        return self._storage.Level(
            tiles=str(self._tilesPath(exponent=exponent)),
            occupancy=str(self._occupancyPath(exponent=exponent)),
            shape=extent,
            tile=tile,
            fill=self._fill,
        )

    def create(self, exponent: int) -> "Pyramid":
        """
        Make the file that holds the level at {exponent}, at its full padded size

        The file is sparse, so this costs nothing until tiles land in it, and a file left
        behind by a build that died starts over. This is the one thing a level needs before
        workers can write tiles into it, so whoever hands out the work does it first
        """
        # make my directory, if this is the first time
        self.home.mkdir(parents=True, exist_ok=True)
        # the layout of the level
        extent, tile, _ = self.layout(exponent=exponent)
        # make the file
        self._storage.Draft.create(
            tiles=str(self._tilesPath(exponent=exponent)), shape=extent, tile=tile
        )
        # all done
        return self

    def draft(self, exponent: int):
        """
        Take hold of the level at {exponent} for writing; the file must exist already
        """
        # the layout of the level
        extent, tile, _ = self.layout(exponent=exponent)
        # map the file
        return self._storage.Draft(
            tiles=str(self._tilesPath(exponent=exponent)), shape=extent, tile=tile
        )

    def holds(self, exponent: int) -> bool:
        """
        Report whether the level at {exponent} exists, without taking hold of it

        A level exists when its occupancy record does and the sidecar describes the layout
        this code reads: the record is the last thing a build writes, so a tile file without
        one is a build in progress or the remains of one that died, and levels written for
        another layout, or by a version of this code that stored them differently, would be
        misread rather than read. Neither is a level, and a build starts them over
        """
        # a sidecar for another layout disowns every level
        if not self._current():
            # so there is nothing here
            return False
        # otherwise, ask the filesystem
        return self._occupancyPath(exponent=exponent).exists()

    def layout(self, exponent: int) -> tuple:
        """
        Report the extent of the level at {exponent}, the tile it is diced into, and the
        shape of its grid of tiles, edge tiles included
        """
        # the extent, halved once per level
        extent = self._extent(exponent=exponent)
        # the tile, clipped to it
        tile = self._tileOf(extent=extent)
        # and the grid of tiles
        grid = tuple((axis + width - 1) // width for axis, width in zip(extent, tile))
        # all done
        return extent, tile, grid

    def commit(self, exponent: int, occupancy: bytearray) -> None:
        """
        Write the occupancy record of the level at {exponent}, which is what makes it exist

        The record lands under a temporary name and is renamed into place, so a reader
        never sees a partial one and a build that dies leaves no record at all
        """
        # where the record goes, and where it is assembled
        final = self._occupancyPath(exponent=exponent)
        partial = final.parent / (final.name + ".partial")
        # write it
        with open(str(partial), "wb") as record:
            # in one piece
            record.write(bytes(occupancy))
        # and move it into place; the rename is atomic, and replaces a stale record
        os.replace(str(partial), str(final))
        # all done
        return

    def remember(self) -> "Pyramid":
        """
        Keep my statistics, and the layout they describe, beside my levels

        The sidecar is what makes the levels readable: without one that describes the
        layout this code reads, the levels beside it are not consulted. So it is written
        even when the raster held nothing to measure
        """
        # the record: the layout, so a reader can tell a cache built for another layout
        # from its own, and the numbers
        record = {
            "format": self.format,
            "cell": self._cell,
            "shape": list(self._shape),
            "tile": list(self._tile),
            "statistics": {part: float(value) for part, value in self._parts().items()},
        }
        # where it goes, and where it is assembled
        final = self.sidecar
        partial = final.parent / (final.name + ".partial")
        # write it
        with open(str(partial), "w") as sidecar:
            # as text anyone can read
            json.dump(record, sidecar, indent=2)
        # and move it into place
        os.replace(str(partial), str(final))
        # all done
        return self

    def recall(self) -> "Pyramid":
        """
        Take back the statistics an earlier run measured while it built my levels
        """
        # numbers i already hold stand
        if self.statistics.count > 0:
            # so there is nothing to take back
            return self
        # the sidecar
        record = self._sidecar()
        # a directory without one, or with one for another layout, holds no numbers of mine
        if record is None:
            # so there is nothing to take back
            return self
        # the numbers
        statistics = record.get("statistics", {})
        # go through the parts of the record
        for part in self._parts():
            # a record that does not carry this part carries none of them
            if part not in statistics:
                # so there is nothing to take back
                return self
        # otherwise, install them
        for part in self._parts():
            # one at a time
            setattr(self.statistics, part, statistics[part])
        # all done
        return self

    def _sidecar(self):
        """
        Read my sidecar, if there is one and it describes the layout this code reads
        """
        # the file
        path = self.sidecar
        # a directory without one has never completed a first level
        if not path.exists():
            # so there is no record
            return None
        # carefully, since the file is text and anyone may have touched it
        try:
            # read it
            with open(str(path), "r") as sidecar:
                # as a record
                record = json.load(sidecar)
        # a file that is not a record is no record
        except (OSError, ValueError) as error:
            # make a channel
            channel = journal.warning("qed.readers.pyramid")
            # complain
            channel.line(f"could not read the sidecar of '{self._name}'")
            channel.line(f"at '{path}'")
            channel.line(f"got: {error}")
            # flush
            channel.log()
            # and report that there is none
            return None
        # a record written for another layout, or by another version of this code, does
        # not describe my levels
        if (
            record.get("format") != self.format
            or record.get("cell") != self._cell
            or tuple(record.get("shape", ())) != self._shape
            or tuple(record.get("tile", ())) != self._tile
        ):
            # so it is no record of mine
            return None
        # hand it back
        return record

    def _current(self) -> bool:
        """
        Report whether the sidecar beside my levels describes the layout this code reads
        """
        # it does when there is a record to be had
        return self._sidecar() is not None

    def _parts(self) -> dict:
        """
        The pieces of my statistical record, by the name each goes by
        """
        # the accumulator carries a population, its extrema, and the running moments
        return {
            part: getattr(self.statistics, part)
            for part in ("count", "min", "mean", "m2", "max")
        }

    def _tilesPath(self, exponent: int):
        """
        The file that holds the tiles of the level at {exponent}
        """
        # the directory already says which dataset this is, so the level says only how deep;
        # two digits, so the levels list in order
        return self.home / f"level-{exponent:02d}.tiles"

    def _occupancyPath(self, exponent: int):
        """
        The record of which tiles of the level at {exponent} were written
        """
        # beside the tiles
        return self.home / f"level-{exponent:02d}.occupancy"

    def _tileOf(self, extent: tuple) -> tuple:
        """
        The tile a level of the given {extent} is diced into

        It is the chunk of the product, so a tile request reads exactly one tile; at the top
        of the pyramid, where the level is smaller than a chunk, the tile shrinks with it
        """
        # clip the chunk to the extent on each axis
        return tuple(min(width, axis) for width, axis in zip(self._tile, extent))

    def _extent(self, exponent: int) -> tuple:
        """
        Report the extent of the level at {exponent}
        """
        # halve the base once per level
        return tuple(axis // 2**exponent for axis in self._shape)

    def _tiles(self, extent: tuple, tile: tuple):
        """
        Walk a level of the given {extent} in tiles of the given {tile}
        """
        # go through the rows
        for row in range(0, extent[0], tile[0]):
            # the rows this tile covers
            height = min(tile[0], extent[0] - row)
            # and the columns
            for col in range(0, extent[1], tile[1]):
                # the columns this tile covers
                width = min(tile[1], extent[1] - col)
                # hand off the tile
                yield (row, col), (height, width)
        # all done
        return

    # public data
    @property
    def workspace(self):
        """
        The workspace my levels live in
        """
        # the one i was handed
        return self._workspace

    @property
    def root(self):
        """
        The directory that holds every pyramid
        """
        # the workspace decides where derived data goes
        return self._workspace.cache(name="pyramids")

    @property
    def home(self):
        """
        The directory that holds my levels
        """
        # the workspace may have nowhere to keep anything
        root = self.root
        # in which case neither do i
        if root is None:
            # so say so
            return None
        # one directory per product version, and within it one per dataset, so that the
        # levels of one dataset are never in the way of another's
        return root.join(self._stamp, *self._path)

    @property
    def sidecar(self):
        """
        The file that describes my levels and carries my statistics
        """
        # beside the levels
        return self.home / "pyramid.json"

    # constants
    # the version of the layout; a sidecar written for another is not read
    format = 1


# end of file
