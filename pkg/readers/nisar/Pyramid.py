# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import hashlib

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
        the product when there is nothing. The cache is opened read only, because many
        workers may be reading the same levels at once and none of them may write
        """
        # where my levels would be
        path = self.path
        # a workspace with nowhere to keep anything, or a product nobody has prepared
        if path is None or not path.exists():
            # has no levels to offer, and this must not be the thing that makes one
            return self
        # otherwise, take hold of what is there
        self._attach(mode="r")
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
        if self._kernels is None:
            # make a channel
            channel = journal.warning("qed.readers.pyramid")
            # explain, since the absence will show as a view that is slow rather than wrong
            channel.line(f"no levels built for '{self._name}'")
            channel.line(f"its cells are encoded, and only a decoder can read them")
            # flush
            channel.log()
            # and leave without building anything
            return self
        # figure out how deep to go
        depth = depth if depth > 0 else self.depth()
        # open the cache for writing
        cache = self._attach(mode="r+")
        # if it could not be opened, the complaint has been lodged
        if cache is None:
            # so there is nothing to do
            return self
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
            extent = [axis // 2 for axis in self._extent(exponent=exponent - 1)]
            # an extent that has collapsed cannot be halved again
            if min(extent) < 1:
                # so this is the top of the pyramid
                break
            # make the level
            level = self._create(cache=cache, exponent=exponent, extent=extent)
            # count the tiles that turn out to hold anything
            written = 0
            # walk it in tiles, which are chunks, so no chunk is written twice
            for origin, shape in self._tiles(extent=extent):
                # and fill each one by decimating the level below; a tile of pure fill is
                # skipped, so the level stays as sparse as the product it came from
                record = self._kernels.decimate(
                    source=source,
                    destination=level,
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
                # count the tiles that held anything
                written += 1 if record[0] else 0
            # record it
            self._levels[exponent] = level
            # show me
            channel.log(
                f"{self._name}: level {exponent} of extent {extent}, "
                f"{written} tiles written"
            )
        # the statistics were measured while the first level was being built, and a level
        # is built once; keep them beside it, or a pyramid found on disk would arrive
        # without the very numbers it was the cheapest way to compute
        self._remember(cache=cache)
        # all done
        return self

    def depth(self) -> int:
        """
        Report how many levels the extent supports: the top of the pyramid is the level
        whose whole raster fits in a single tile
        """
        # start at the base
        extent = list(self._shape)
        # and the tile it is chopped into
        tile = self._tile
        # count the halvings
        levels = 0
        # until the raster fits in one tile
        while any(axis > width for axis, width in zip(extent, tile)):
            # halve it
            extent = [axis // 2 for axis in extent]
            # an extent that has collapsed cannot be halved again
            if min(extent) < 1:
                # so stop
                break
            # count the level
            levels += 1
        # hand off the count
        return levels

    def close(self) -> "Pyramid":
        """
        Release the cache file
        """
        # if i am attached
        if self._cache is not None:
            # let it go
            self._cache.close()
            # and forget it
            self._cache = None
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
        self._base = dataset.data.dataset
        # the kernels that read cells of this type. a raster whose samples are encoded
        # rather than stored has none, and it must not get levels: decimation is a read and
        # a write, and a read into a buffer laid out for the wrong cell type deposits
        # something that is not the data
        self._kernels = dataset.kernels
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
        # every value it can hold is a measurement
        else:
            # so whatever the product declared stands, and nothing ever reads it back
            self._fill = self._base.fillValue
        # the identity of the product this dataset came from, so a cache built against one
        # version of a file is never read against another
        self._stamp = self._identify(reader=reader, uri=dataset.uri)
        # where the cache lives is not mine to decide: the workspace the application owns
        # is the one authority on where derived data goes, and it is handed to me
        self._workspace = workspace
        # the file, once attached, and the levels it holds
        self._cache = None
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

    def _attach(self, mode: str):
        """
        Open the cache file, making it and its directory on first use
        """
        # if i am already attached
        if self._cache is not None:
            # hand it back
            return self._cache
        # the file that holds my levels
        path = self.path
        # a workspace that could not make its cache has already complained
        if path is None:
            # so there is nowhere to keep anything
            return None
        # carefully, since the cache lives on a filesystem that may refuse us
        try:
            # open the file, making it if this is the first time
            cache = qed.h5.libh5.File(str(path), mode if path.exists() else "w")
        # if anything goes wrong
        except Exception as error:
            # make a channel
            channel = journal.warning("qed.readers.pyramid")
            # complain
            channel.line(f"could not open the pyramid cache of '{self._name}'")
            channel.line(f"at '{path}'")
            channel.line(f"got: {error}")
            # flush
            channel.log()
            # and report that there is none
            return None
        # remember it
        self._cache = cache
        # take stock of the levels it already holds
        self._levels = self._survey(cache=cache)
        # and of what an earlier run measured while it built them
        self._recall(cache=cache)
        # hand it off
        return cache

    def _survey(self, cache) -> dict:
        """
        Find the levels the cache already holds
        """
        # the pile
        levels = {}
        # walk to my group, without making one
        group = self._openGroup(cache=cache, make=False)
        # a cache that has never held my levels has nothing to report
        if group is None:
            # so the pile stays empty
            return levels
        # go through the levels the extent could support
        for exponent in range(1, self.depth() + 1):
            # the name this level goes by within the group
            name = self._levelName(exponent=exponent)
            # if the group does not have it
            if not group.has(name=name):
                # neither do i
                continue
            # otherwise, take hold of it
            levels[exponent] = group.dataset(path=name)
        # hand off the pile
        return levels

    def _create(self, cache, exponent: int, extent: list):
        """
        Make the dataset that holds one level
        """
        # the chunk of a level is the tile the client asks for, so a request reads exactly
        # one chunk and decompresses nothing it does not use; at the top of the pyramid,
        # where the raster is smaller than a tile, the chunk shrinks with it
        chunk = [min(width, axis) for width, axis in zip(self._tile, extent)]
        # start the creation plan
        dcpl = qed.h5.libh5.properties.dcpl()
        dcpl.chunk = chunk
        # cells nobody writes must read back exactly the way the product spells absence.
        # there is no freedom here: the library's own default is zero, and zero is a
        # perfectly good measurement, so a level built over that default would hand the
        # level above it a raster with no fill in it at all, and the pyramid would densify
        # one step at a time. the product is the only authority on what its absence looks
        # like, so ask it rather than assume
        if self._fill is not None:
            # adopt it
            dcpl.fillValue = self._fill
        # a level is derived data we will read far more often than we write, and the
        # products it comes from are compressed; store it the same way, or a pyramid of a
        # sparse product ends up larger than the product. shuffle first, which groups the
        # bytes of like significance and is what makes deflate worth running on floats
        dcpl.addShuffle()
        dcpl.addDeflate(self.compression)
        # a compressed chunk cannot be touched without decompressing all of it, so the
        # library must be able to hold whole chunks; its default is a single megabyte,
        # which does not fit even one chunk of a complex product, and every access would
        # pay to inflate what the last one just discarded
        dapl = qed.h5.libh5.properties.dapl()
        dapl.chunkCache = qed.h5.libh5.properties.ChunkCache(
            slots=self.slots,
            bytes=self.slots * self._chunkBytes(chunk=chunk),
            preemption=0.75,
        )
        # make it, in the group that says which dataset it belongs to
        return self._openGroup(cache=cache, make=True).create(
            path=self._levelName(exponent=exponent),
            type=self._datatype,
            space=qed.h5.libh5.DataSpace(extent),
            dcpl=dcpl,
            dapl=dapl,
        )

    def _chunkBytes(self, chunk: list) -> int:
        """
        Report how much memory one chunk of {chunk} cells occupies
        """
        # the cells of the chunk
        cells = 1
        # by going through its axes
        for width in chunk:
            # and multiplying them out
            cells *= width
        # each cell is a complex pair of singles; ask the type rather than assume
        return cells * self._datatype.bytes

    def _remember(self, cache) -> "Pyramid":
        """
        Keep my statistics beside my levels
        """
        # nothing was measured, so there is nothing to keep
        if self.statistics.count == 0:
            # leave the cache alone
            return self
        # the group my levels live in
        group = self._openGroup(cache=cache, make=True)
        # go through the parts of the record
        for part, value in self._parts().items():
            # each one hangs on the group, which already says which dataset it describes
            name = part
            # a number already there was written by the run that built the levels
            if group.hasAttribute(name=name):
                # and a level is built once, so it still stands
                continue
            # otherwise, make the attribute
            attribute = group.createAttribute(
                name=name,
                type=qed.h5.memtypes.double.htype,
                space=qed.h5.libh5.DataSpace([]),
            )
            # and record the number
            attribute.double(float(value))
        # all done
        return self

    def _recall(self, cache) -> "Pyramid":
        """
        Take back the statistics an earlier run measured while it built my levels
        """
        # walk to my group, without making one
        group = self._openGroup(cache=cache, make=False)
        # a cache that has never held my levels holds no numbers either
        if group is None:
            # so there is nothing to take back
            return self
        # go through the parts of the record
        for part in self._parts():
            # a group that does not carry this part carries none of them
            if not group.hasAttribute(name=part):
                # so there is nothing to take back
                return self
            # otherwise, install it
            setattr(self.statistics, part, group.getAttribute(name=part).double())
        # all done
        return self

    def _parts(self) -> dict:
        """
        The pieces of my statistical record, by the name each goes by
        """
        # the accumulator carries a population, its extrema, and the running moments
        return {
            part: getattr(self.statistics, part)
            for part in ("count", "min", "mean", "m2", "max")
        }

    def _levelName(self, exponent: int) -> str:
        """
        Build the name a level goes by within its group
        """
        # the group already says which dataset this is, so the level says only how deep
        return f"level{exponent}"

    def _openGroup(self, cache, make: bool):
        """
        Walk to the group that holds my levels, making it when asked to
        """
        # start at the root of the cache
        group = cache
        # and walk one coordinate at a time, so the file has the shape of the selector
        # rather than one flat name per dataset with the whole selector spelled into it
        for step in self._path:
            # a step that is already there is walked into
            if group.has(name=step):
                # by opening it
                group = group.group(path=step)
                # and moving on
                continue
            # a step that is missing ends the walk, unless i am building
            if not make:
                # in which case there is no group
                return None
            # otherwise, make it
            group = group.create(path=step)
        # hand back where the walk ended
        return group

    def _extent(self, exponent: int) -> tuple:
        """
        Report the extent of a level
        """
        # halve the base once per level
        return tuple(axis // 2**exponent for axis in self._shape)

    def _tiles(self, extent: list):
        """
        Walk a level in tiles, which are its chunks
        """
        # the tile, kept inside the extent on both axes
        tile = [min(width, axis) for width, axis in zip(self._tile, extent)]
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
    def root(self):
        """
        The directory that holds my cache
        """
        # the workspace decides where derived data goes
        return self._workspace.cache(name="pyramids")

    @property
    def path(self):
        """
        The file that holds my levels
        """
        # the workspace may have nowhere to keep anything
        root = self.root
        # in which case neither do i
        if root is None:
            # so say so
            return None
        # one cache per product version, holding the levels of all its datasets
        return root / f"{self._stamp}.h5"

    # constants
    # how hard to squeeze a level; the levels are written once and read many times, so a
    # middling setting buys most of the space at a fraction of the time the highest costs
    compression = 4
    # how many chunks the library may hold for one level; a decimation reads a two by two
    # block of the level below for every chunk it writes, so a handful is enough to keep
    # any of them from being inflated twice
    slots = 8


# end of file
