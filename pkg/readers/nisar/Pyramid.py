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
    def level(self, zoom: int) -> tuple:
        """
        Report the source that serves a view at {zoom}, and the stride still to apply to it

        A request always gets an answer: the deepest level at or below the one it asked for,
        with whatever decimation remains. With no levels at all that is the base at the full
        stride, which is exactly what the reader did before any of this existed
        """
        # the base serves itself, undecimated
        if zoom <= 0:
            # so hand it back
            return self._base, 1
        # look for the level that matches, then for progressively shallower ones
        for candidate in range(zoom, 0, -1):
            # if i hold this one
            if candidate in self._levels:
                # it serves the request, with whatever decimation is left over
                return self._levels[candidate], 2 ** (zoom - candidate)
        # nothing was built, so the base answers at the full stride
        return self._base, 2**zoom

    def build(self, depth: int = 0) -> "Pyramid":
        """
        Make the levels up to {depth}, or as many as the extent supports

        Level 1 is the only one that reads the product; every level after it is built from
        the one above at a quarter the size, so the whole pyramid costs about a third more
        than the single pass that built its first level
        """
        # figure out how deep to go
        depth = depth if depth > 0 else self.depth()
        # open the cache for writing
        cache = self._attach(mode="a")
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
            source, _ = self.level(zoom=exponent - 1)
            # its extent, half the one below it on each axis
            extent = [axis // 2 for axis in self._extent(exponent=exponent - 1)]
            # an extent that has collapsed cannot be halved again
            if min(extent) < 1:
                # so this is the top of the pyramid
                break
            # make the level
            level = self._create(cache=cache, exponent=exponent, extent=extent)
            # count what the level turns out to hold
            cells, written = 0, 0
            # walk it in tiles, which are chunks, so no chunk is written twice
            for origin, shape in self._tiles(extent=extent):
                # and fill each one by decimating the level below; a tile of pure fill is
                # skipped, so the level stays as sparse as the product it came from
                yields = qed.libqed.nisar.decimate(
                    source=source,
                    destination=level,
                    datatype=self._datatype,
                    origin=origin,
                    shape=shape,
                    stride=(2, 2),
                )
                # fold in what it deposited
                cells += yields
                # counting the tiles that held anything
                written += 1 if yields else 0
            # record it
            self._levels[exponent] = level
            # show me
            channel.log(
                f"{self._name}: level {exponent} of extent {extent}, "
                f"{written} tiles written, {cells} cells"
            )
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
    def __init__(self, dataset, workspace, **kwds):
        # chain up
        super().__init__(**kwds)
        # remember what i am a pyramid of
        self._name = dataset.pyre_name
        self._shape = tuple(dataset.shape)
        self._tile = tuple(dataset.tile)
        self._datatype = dataset.datatype.htype
        self._base = dataset.data.dataset
        # what the product writes where it has nothing to say; a dataset made without one
        # reports nothing, and then my levels are made without one too, so the two still
        # agree
        self._fill = self._base.fillValue
        # the identity of the product this dataset came from, so a cache built against one
        # version of a file is never read against another
        self._stamp = self._identify(uri=dataset.uri)
        # where the cache lives is not mine to decide: the workspace the application owns
        # is the one authority on where derived data goes, and it is handed to me
        self._workspace = workspace
        # the file, once attached, and the levels it holds
        self._cache = None
        self._levels = {}
        # all done
        return

    # implementation details
    def _identify(self, uri) -> str:
        """
        Build a stamp that identifies the exact bytes this pyramid was derived from
        """
        # the address of the product
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
        # hand it off
        return cache

    def _survey(self, cache) -> dict:
        """
        Find the levels the cache already holds
        """
        # the pile
        levels = {}
        # go through the levels the extent could support
        for exponent in range(1, self.depth() + 1):
            # the name this level would go by
            name = self._levelName(exponent=exponent)
            # if the cache does not have it
            if not cache.has(name=name):
                # neither do i
                continue
            # otherwise, take hold of it
            levels[exponent] = cache.dataset(path=name)
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
        # make it
        return cache.create(
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

    def _levelName(self, exponent: int) -> str:
        """
        Build the name a level goes by inside the cache
        """
        # the cache holds one product, whose dataset names are already distinct, so the
        # levels live in a flat namespace: no groups to create, and membership is a
        # direct lookup
        return f"{self._name}.level{exponent}"

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
