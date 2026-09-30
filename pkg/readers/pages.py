# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import collections
import statistics
import struct
import sys
import zlib

# support
import qed

# the share of its raw size below which a written chunk counts as nearly empty: such a chunk
# holds almost nothing but the fill value, and costs a reader as much as a full one
NEARLY_EMPTY = 0.01
# the number of bins of the histograms, each covering an equal share of the range
BINS = 10
# the states of the cells of a chunk grid, in the order of their codes
STATES = ("unwritten", "fill", "sliver", "data")
# the layout of a cell, by the name of its pyre memory cell
LAYOUTS = {
    "int8": "b",
    "uint8": "B",
    "int16": "h",
    "uint16": "H",
    "int32": "i",
    "uint32": "I",
    "int64": "q",
    "uint64": "Q",
    "float32": "f",
    "float64": "d",
    "complex64": "ff",
    "complex128": "dd",
}


def occupancy(*, tables: dict, name: str, pageSize: int, raw: int, tile: tuple, grid: int) -> dict:
    """
    Describe how the chunks of the dataset {name} sit on the pages of its file, given the chunk
    {tables} of every dataset in the file as lists of (address, bytes, origin), the {pageSize},
    the {raw} size of a chunk, the {tile} shape of a chunk, and the number of chunks in the
    {grid} the tiling describes

    A reader that fetches whole pages, e.g. the HDF5 driver for S3, moves every byte of every
    page it touches; the record says how many of those bytes the dataset needs, alone and
    together with the datasets that share its pages
    """
    # the chunks of the dataset
    chunks = tables[name]
    # the stored sizes, in order
    sizes = sorted(size for _, size, _ in chunks)
    # their total
    stored = sum(sizes)
    # start the record with what does not need pages
    record = {
        "dataset": name,
        "grid": grid,
        "written": len(chunks),
        "stored": stored,
        "raw": raw,
        "median": statistics.median(sizes) if sizes else None,
        "smallest": sizes[0] if sizes else None,
        "largest": sizes[-1] if sizes else None,
        "compression": raw * len(sizes) / stored if stored else None,
        "empty": sum(1 for size in sizes if size < NEARLY_EMPTY * raw),
        "emptyStored": sum(size for size in sizes if size < NEARLY_EMPTY * raw),
        "sizes": histogram(values=[size / raw for size in sizes]),
        "pageSize": pageSize,
    }
    # a file without pages, or a dataset with nothing written, has no pages to describe
    if not pageSize or not chunks:
        # so the record is complete
        return record
    # the bytes each dataset has on each page
    pages = collections.defaultdict(collections.Counter)
    # and the number of chunks, of any dataset, that touch each page
    crowd = collections.Counter()
    # go through every dataset in the file
    for other, table in tables.items():
        # and each of its chunks
        for address, size, _ in table:
            # apportion its bytes among the pages it lands on
            for page, share in apportion(address=address, size=size, pageSize=pageSize):
                # by adding them to the page
                pages[page][other] += share
                # and counting the chunk among its tenants
                crowd[page] += 1
    # the pages this dataset touches
    mine = sorted(page for page, tenants in pages.items() if name in tenants)
    # and the ones among them that hold at least one of its chunks that is not nearly empty
    substantive = {
        page
        for address, size, _ in chunks
        if size >= NEARLY_EMPTY * raw
        for page, _ in apportion(address=address, size=size, pageSize=pageSize)
    }
    # the number of pages each of its chunks spans
    spans = [
        (address + size - 1) // pageSize - address // pageSize + 1 for address, size, _ in chunks
    ]
    # the share of each of its pages that it fills
    fill = [pages[page][name] / pageSize for page in mine]
    # and the share filled by everybody
    total = [sum(pages[page].values()) / pageSize for page in mine]
    # the datasets that share its pages, and the bytes they have on them
    partners = collections.Counter()
    # go through its pages
    for page in mine:
        # and their tenants
        for other, share in pages[page].items():
            # everybody else is a partner
            if other != name:
                # with a share of the page
                partners[other] += share
    # the group that reads together: the dataset and its partners
    group = {name, *partners}
    # the pages the group touches
    joint = [page for page, tenants in pages.items() if group & tenants.keys()]
    # the bytes the group stores
    together = sum(size for other in group for _, size, _ in tables[other])
    # complete the record
    record.update(
        {
            # the pages and how the chunks span them
            "pages": len(mine),
            "spans": collections.Counter(min(span, 3) for span in spans),
            # the bytes moved per byte needed, reading the chunks one at a time
            "alone": sum(spans) * pageSize / stored,
            # reading every chunk, with each page fetched once
            "once": len(mine) * pageSize / stored,
            # the pages a reader of the dataset fetches for nothing but its nearly empty chunks
            "emptyPages": len(mine) - len(substantive),
            # and reading it together with its partners, with each page fetched once
            "joint": len(joint) * pageSize / together,
            "partners": dict(partners),
            # the fill of its pages, by the dataset and by everybody
            "fillMedian": statistics.median(fill),
            "fillMean": statistics.fmean(fill),
            "fillFull": sum(1 for share in fill if share >= 0.9) / len(fill),
            "fill": histogram(values=fill),
            "totalMean": statistics.fmean(total),
            "total": histogram(values=total),
            # how crowded the pages are, in chunks of any dataset
            "tenants": statistics.median(crowd[page] for page in mine),
            # whether chunks that share a page are neighbors on the raster
            "locality": locality(chunks=chunks, pageSize=pageSize, tile=tile),
        }
    )
    # hand off the record
    return record


def strip(*, tables: dict, name: str, pageSize: int):
    """
    Describe the pages the chunks of the dataset {name} land on, in file order, given the chunk
    {tables} of every dataset in the file and the {pageSize}: for each page, the bytes of the
    dataset, the number of its chunks, the bytes of all the other datasets together, and the
    other dataset with the most bytes on it; {None} for a file that is not paged

    The description is a set of parallel lists, one entry per page
    """
    # a file without pages
    if not pageSize:
        # has nothing to describe
        return None
    # the bytes of the dataset on each of its pages, and the number of its chunks on each
    mine = collections.Counter()
    count = collections.Counter()
    # go through its chunks
    for address, size, _ in tables[name]:
        # and the pages each one lands on
        for page, share in apportion(address=address, size=size, pageSize=pageSize):
            # add its bytes
            mine[page] += share
            # and count it
            count[page] += 1
    # the bytes of every other dataset on those pages
    others = collections.defaultdict(collections.Counter)
    # go through the other datasets
    for other, table in tables.items():
        # skipping this one
        if other == name:
            # by moving on
            continue
        # go through their chunks
        for address, size, _ in table:
            # and the pages each one lands on
            for page, share in apportion(address=address, size=size, pageSize=pageSize):
                # the pages of the dataset are the only ones of interest
                if page in mine:
                    # record the share
                    others[page][other] += share
    # the pages, in file order
    pages = sorted(mine)
    # the largest other tenant of each page
    largest = [others[page].most_common(1)[0] if others[page] else ("", 0) for page in pages]
    # hand off the description
    return {
        "pages": pages,
        "mine": [mine[page] for page in pages],
        "chunks": [count[page] for page in pages],
        "others": [sum(others[page].values()) for page in pages],
        "partner": [partner for partner, _ in largest],
        "partnerBytes": [share for _, share in largest],
    }


def filemap(*, tables: dict, name: str, pageSize: int, fileBytes: int = None):
    """
    Describe every page of a file with pages of {pageSize}, given the chunk {tables} of every
    dataset in it: for each page, the bytes and the number of chunks of each raster of the
    product, and the bytes of all the datasets the product does not display; the raster {name}
    is the one in view; {None} for a file that is not paged

    The rasters are the datasets filed under their names rather than their paths in the file;
    each gets dense lists with one entry per page, so the room left on a page is what the
    metadata and the free space take
    """
    # a file without pages
    if not pageSize:
        # has nothing to describe
        return None
    # the rasters of the product, in the order of its reader
    rasters = [other for other in tables if not other.startswith("/")]
    # the last page any chunk reaches
    last = max(
        (
            (address + size - 1) // pageSize
            for table in tables.values()
            for address, size, _ in table
        ),
        default=-1,
    )
    # the pages of the file: as many as its size spans, or as the chunks reach when it is unknown
    count = max(-(-fileBytes // pageSize) if fileBytes else 0, last + 1)
    # the bytes and the chunks of each raster on each page
    mine = {raster: [0] * count for raster in rasters}
    chunks = {raster: [0] * count for raster in rasters}
    # and the bytes of everything else on each page
    others = [0] * count
    # go through every dataset in the file
    for other, table in tables.items():
        # find out whether it is a raster of the product
        raster = other in mine
        # go through its chunks
        for address, size, _ in table:
            # and the pages each one lands on
            for page, share in apportion(address=address, size=size, pageSize=pageSize):
                # a dataset the product does not display
                if not raster:
                    # adds its bytes to everybody else
                    others[page] += share
                    # and nothing more
                    continue
                # a raster adds its bytes to its own account
                mine[other][page] += share
                # and counts its chunk
                chunks[other][page] += 1
    # hand off the description
    return {
        "pages": count,
        "rasters": [
            {"name": raster, "bytes": mine[raster], "chunks": chunks[raster]} for raster in rasters
        ],
        "selected": rasters.index(name) if name in mine else None,
        "others": others,
    }


def states(
    *, table: list, shape: tuple, tile: tuple, raw: int, fill: int = None, pageSize: int = 0
) -> dict:
    """
    Classify the cells of the chunk grid of a raster of {shape} in chunks of {tile}, given its
    chunk {table} as a list of (address, bytes, origin), the {raw} size of a chunk, and the
    stored size of a chunk that holds nothing but the {fill}, if any: a cell is unwritten, fill,
    a sliver that holds a little data among the fill, or data

    The grid is described in row major order, by the code of the state of each cell, its index in
    {STATES}, the stored size of its chunk, zero for the cells never written, and, in a file with
    pages of {pageSize}, the page its chunk starts on, -1 for the cells never written
    """
    # unpack the shape and the tile
    rows, cols = shape
    tileRows, tileCols = tile
    # the extent of the grid
    gridRows = -(-rows // tileRows)
    gridCols = -(-cols // tileCols)
    # every cell starts out unwritten
    codes = [0] * (gridRows * gridCols)
    sizes = [0] * (gridRows * gridCols)
    pages = [-1] * (gridRows * gridCols)
    # go through the written chunks
    for address, size, (row, col) in table:
        # the cell of the chunk
        cell = (row // tileRows) * gridCols + col // tileCols
        # a chunk of the size of the fill holds nothing but the fill
        if fill is not None and size == fill:
            # so mark it
            codes[cell] = 1
        # a nearly empty chunk that is not all fill holds a sliver of data
        elif size < NEARLY_EMPTY * raw:
            # so mark it
            codes[cell] = 2
        # and everything else holds data
        else:
            # so mark it
            codes[cell] = 3
        # record its size
        sizes[cell] = size
        # and the page it starts on, when the file has pages
        pages[cell] = address // pageSize if pageSize else -1
    # hand off the grid
    return {"rows": gridRows, "cols": gridCols, "codes": codes, "sizes": sizes, "pages": pages}


def apportion(*, address: int, size: int, pageSize: int):
    """
    Generate the pages a chunk of {size} bytes at {address} lands on, with its bytes on each
    """
    # the pages it lands on
    first = address // pageSize
    last = (address + size - 1) // pageSize
    # go through them
    for page in range(first, last + 1):
        # the part of the chunk that falls on this page
        start = max(address, page * pageSize)
        end = min(address + size, (page + 1) * pageSize)
        # hand it off
        yield page, end - start
    # all done
    return


def locality(*, chunks: list, pageSize: int, tile: tuple):
    """
    The share of the pairs of chunks that follow each other on a page and are also neighbors
    on the raster, or {None} when no page holds two chunks of the dataset
    """
    # the tile shape, which separates neighbors on the raster
    rows, cols = tile
    # the chunks in the order they sit in the file
    ordered = sorted(chunks)
    # the pairs that share a page, and the ones among them that are neighbors
    pairs = 0
    neighbors = 0
    # go through consecutive chunks
    for (before, _, (r0, c0)), (after, _, (r1, c1)) in zip(ordered, ordered[1:]):
        # if they are on different pages
        if before // pageSize != after // pageSize:
            # they are not a pair
            continue
        # count the pair
        pairs += 1
        # and note whether they touch along a row or a column of the tiling
        neighbors += (abs(r1 - r0), abs(c1 - c0)) in ((rows, 0), (0, cols))
    # hand off the share, if there is one
    return neighbors / pairs if pairs else None


def decode(*, stored: bytes, filters: list, mask: int, cell: int) -> bytes:
    """
    Undo the {filters} a chunk of cells {cell} bytes wide went through on its way to its
    {stored} bytes, skipping the ones whose bit is set in the filter {mask}, or return {None}
    when one of them is a filter this function does not know how to undo
    """
    # the bytes, as they come through each stage
    data = stored
    # the filters were applied in order, so undo them in reverse
    for index, name in reversed(list(enumerate(filters))):
        # the library skips a filter that fails on a chunk and says so in the mask
        if mask & (1 << index):
            # so this one has nothing to undo
            continue
        # deflate
        if name == "deflate":
            # inflates
            data = zlib.decompress(data)
            # and moves on
            continue
        # the shuffle
        if name == "shuffle":
            # gathered byte k of every cell into plane k, so interleave the planes again
            data = unshuffle(data=data, cell=cell)
            # and move on
            continue
        # anything else is beyond me
        return None
    # hand off the cells
    return data


def encode(*, data: bytes, filters: list, cell: int, level: int) -> bytes:
    """
    Pass the chunk {data}, of cells {cell} bytes wide, through {filters} in order, deflating at
    {level}, or return {None} when one of them is a filter this function does not know
    """
    # the bytes, as they come through each stage
    encoded = data
    # go through the filters in order
    for name in filters:
        # deflate
        if name == "deflate":
            # compresses
            encoded = zlib.compress(encoded, level)
            # and moves on
            continue
        # the shuffle
        if name == "shuffle":
            # gathers byte k of every cell into plane k
            encoded = shuffle(data=encoded, cell=cell)
            # and moves on
            continue
        # anything else is beyond me
        return None
    # hand off the stored bytes
    return encoded


def shuffle(*, data: bytes, cell: int) -> bytes:
    """
    Shuffle the bytes of {data}, whose cells are {cell} bytes wide: byte k of every cell goes to
    plane k, and any bytes past the last whole cell stay as they are
    """
    # single byte cells are left alone
    if cell == 1:
        # so there is nothing to do
        return data
    # the number of whole cells
    count = len(data) // cell
    # gather the planes, and keep the leftover bytes at the end
    return b"".join(data[k : cell * count : cell] for k in range(cell)) + data[cell * count :]


def unshuffle(*, data: bytes, cell: int) -> bytes:
    """
    Undo the byte shuffle of {data}, whose cells are {cell} bytes wide: the shuffle stores byte
    k of every cell in plane k, and any bytes past the last whole cell as they were
    """
    # single byte cells are left alone by the shuffle
    if cell == 1:
        # so there is nothing to do
        return data
    # the number of whole cells
    count = len(data) // cell
    # the cells, reassembled
    cells = bytearray(len(data))
    # go through the planes, one per byte of a cell
    for k in range(cell):
        # and put each one back in its place: every {cell} bytes, starting at byte {k}
        cells[k : cell * count : cell] = data[k * count : (k + 1) * count]
    # the leftover bytes stay where they were
    cells[cell * count :] = data[cell * count :]
    # hand off the cells
    return bytes(cells)


def uniform(*, data: bytes, cell: int) -> bytes:
    """
    The one cell, {cell} bytes wide, that every cell of {data} repeats, or {None} if they
    differ
    """
    # the first cell
    first = data[:cell]
    # is the answer if repeating it reproduces the data
    return first if first * (len(data) // cell) == data else None


def interpret(*, data: bytes, cell: str, swapped: bool = False):
    """
    The value of the one {cell} in {data}, whose bytes are in the order the host lacks when
    {swapped}, or {None} for a cell whose layout is unknown
    """
    # the layout of the cell
    layout = LAYOUTS.get(cell)
    # an unknown cell
    if layout is None:
        # has no value to tell
        return None
    # the byte order: the host's, unless swapped
    order = "<" if (sys.byteorder == "little") != swapped else ">"
    # unpack the parts
    parts = struct.unpack(order + layout, data)
    # a pair of parts is a complex number, and a lone part is the value
    return complex(*parts) if len(parts) == 2 else parts[0]


def paging(*, reader):
    """
    Read the page size, the file space strategy, and the size of the file behind {reader}, as a
    tuple, or {None} when it is not an HDF5 product; the page size of a file that is not paged is
    zero, whatever the library reports
    """
    # only the HDF5 readers have pages
    if not isinstance(reader, qed.readers.nisar.h5):
        # so everybody else has no layout
        return None
    # the file creation properties are only reachable through the file itself, so open it
    # again, with the same credentials; this reads nothing but metadata
    h5 = qed.h5.reader(uri=reader.uri, credentials=reader.grant())
    # get the creation properties
    fcpl = h5._file._pyre_id.fcpl
    # and the free space strategy among them
    strategy = fcpl.filespaceStrategy.strategy.name
    # the library reports its default page size for a file of any strategy, but only a file with
    # the paged strategy is laid out in pages; for the rest, a reader fetches what it needs
    pageSize = fcpl.pageSize if strategy == "page" else 0
    # hand off what matters, with the size of the file, if the library can tell
    return pageSize, strategy, h5._file._pyre_id.bytes


def describe(*, dataset, tables: dict, paging: tuple) -> dict:
    """
    Describe how the raster {dataset} sits in its file, given the storage {tables} of every
    dataset in the file and its {paging}: its storage settings, how its chunks sit on the pages,
    what it holds where there is no data, the states of the cells of its chunk grid, and what
    every page of the file holds
    """
    # unpack the paging
    pageSize, strategy, fileBytes = paging
    # the name of the dataset
    name = dataset.pyre_name
    # unpack the extent
    rows, cols = tuple(dataset.shape)
    # a dataset stored in chunks is tiled by them, and any other is one tile
    chunked = dataset.data.dataset.dcpl.layout.name == "chunked"
    # unpack the tile
    tileRows, tileCols = tuple(dataset.tile) if chunked else (rows, cols)
    # the size of a chunk before the filters had their way with it
    raw = tileRows * tileCols * dataset.data.disktype.bytes
    # the number of chunks the tiling describes
    grid = -(-rows // tileRows) * -(-cols // tileCols)
    # describe how it sits on the pages
    record = occupancy(
        tables=tables,
        name=name,
        pageSize=pageSize,
        raw=raw,
        tile=(tileRows, tileCols),
        grid=grid,
    )
    # the storage of the dataset: the file, its shape, the shape of its chunks, its cells, and
    # the filters its chunks pass through, in the order they are applied
    settings = {
        "strategy": strategy,
        "bytes": fileBytes,
        "shape": (rows, cols),
        "tile": (tileRows, tileCols),
        "cell": dataset.cell.pyre_family().rsplit(".", 1)[-1],
        "filters": [entry.name for entry in dataset.data.dataset.dcpl.filters],
    }
    # what the dataset declares it holds where there is nothing, and what it really holds
    fill = nodata(dataset=dataset, table=tables[name], raw=raw)
    # the stored size of a chunk that holds nothing but the fill, when there are such chunks
    size = min(chunk[1] for chunk in tables[name]) if fill["fillChunks"] else None
    # classify the cells of the chunk grid
    cells = states(
        table=tables[name],
        shape=(rows, cols),
        tile=(tileRows, tileCols),
        raw=raw,
        fill=size,
        pageSize=pageSize,
    )
    # hand off the description
    return {
        "name": name,
        "raw": raw,
        "grid": grid,
        "storage": settings,
        "record": record,
        "nodata": fill,
        "states": cells,
        "strip": strip(tables=tables, name=name, pageSize=pageSize),
        "filemap": filemap(tables=tables, name=name, pageSize=pageSize, fileBytes=fileBytes),
    }


def tables(*, reader) -> dict:
    """
    Read the chunk table of every dataset of {reader} as lists of (address, bytes, origin),
    together with the storage of every other dataset in its file, since they all share the
    pages; the datasets the reader does not know are filed under their path in the file
    """
    # the tables, by dataset name
    tables = {}
    # the addresses of the chunks the reader knows about
    known = set()
    # go through the datasets of the reader
    for dataset in reader.datasets:
        # the dataset, as the library sees it
        h5 = dataset.data.dataset
        # the chunks that were written
        table = h5.chunkTable()
        # record them, or, for a dataset that is not stored in chunks, its one extent, which
        # is the whole raster
        tables[dataset.pyre_name] = (
            [(chunk.address, chunk.bytes, tuple(chunk.origin)) for chunk in table]
            if table is not None
            else [(h5.offset, h5.disksize, (0, 0))] if h5.disksize else []
        )
        # remember where they are
        known.update(address for address, _, _ in tables[dataset.pyre_name])
    # open the file again, with the same credentials; this reads nothing but metadata
    h5 = qed.h5.reader(uri=reader.uri, credentials=reader.grant())
    # go through every dataset in it
    for path, extents in storage(group=h5._file._pyre_id, path=""):
        # skip the ones the reader knows about
        if extents and extents[0][0] in known:
            # by moving on
            continue
        # and file the rest, if they occupy any space
        if extents:
            # under their path
            tables[path] = extents
    # hand off the tables
    return tables


def storage(*, group, path: str):
    """
    Generate the path and the storage, as a list of (address, bytes, origin), of every
    dataset under {group}, which sits at {path} in its file
    """
    # go through the members of the group
    for name in group.members():
        # get the member
        member = group.get(path=name)
        # its path
        where = f"{path}/{name}"
        # the kind of object it is
        kind = member.objectType.name
        # a group
        if kind == "group":
            # holds more
            yield from storage(group=member, path=where)
            # and nothing else
            continue
        # anything else that is not a dataset has no storage
        if kind != "dataset":
            # so move on
            continue
        # the chunks of a chunked dataset
        table = member.chunkTable()
        # a dataset stored in chunks
        if table is not None:
            # occupies the places its chunks do
            yield where, [(chunk.address, chunk.bytes, tuple(chunk.origin)) for chunk in table]
            # and nothing else
            continue
        # a compact dataset lives in its object header, among the metadata
        if member.dcpl.layout.name != "contiguous":
            # so it has no storage of its own
            continue
        # a contiguous one occupies one extent, once it is written
        yield where, [(member.offset, member.disksize, None)] if member.disksize else []
    # all done
    return


def nodata(*, dataset, table: list, raw: int) -> dict:
    """
    Compare what {dataset} declares it holds where there is nothing with what the smallest
    of the chunks in its {table} really holds, and time decoding that chunk against making
    it from its value, which is what the library does for a chunk that was never written,
    and against decoding a typical chunk of data, one of {raw} bytes before compression
    """
    # the dataset, as the library sees it
    h5 = dataset.data.dataset
    # its fill value status
    status = h5.dcpl.fillValueStatus.name
    # the fill value the library hands out for chunks that were never written
    hdf5 = h5.fillValue
    # the fill value the conventions of the format declare, if any
    cf = attribute(h5=h5, name="_FillValue")
    # start the record
    nodata = {
        "status": status,
        "hdf5": hdf5,
        "cf": cf,
        "found": None,
        "decode": None,
        "make": None,
        "data": None,
        "fillChunks": None,
        "fillBytes": None,
        "verified": None,
        "level": None,
        "encode": None,
    }
    # without chunks, or with a dataset that is not stored in chunks
    if not table or h5.dcpl.layout.name != "chunked":
        # there is nothing else to say
        return nodata
    # the size of a cell
    width = dataset.cell.bytes
    # the chunks that are not nearly empty, by size
    full = sorted(
        (chunk for chunk in table if chunk[1] >= NEARLY_EMPTY * raw),
        key=lambda chunk: chunk[1],
    )
    # if there are any
    if full:
        # time decoding the median one, which is what a chunk of data costs
        _, nodata["data"] = fetch(h5=h5, origin=full[len(full) // 2][2], cell=width)
    # the smallest chunk is the one most likely to hold nothing but the fill
    _, _, origin = min(table, key=lambda chunk: chunk[1])
    # decode it
    data, seconds = fetch(h5=h5, origin=origin, cell=width)
    # a chunk that went through a filter the decoder does not know
    if data is None:
        # holds something that cannot be told
        nodata["found"] = "unknown"
        # and there is nothing else to say
        return nodata
    # the one cell every cell of the chunk repeats, if there is one
    cell = uniform(data=data, cell=width)
    # a chunk with different cells
    if cell is None:
        # holds data
        nodata["found"] = "data"
        # and there is nothing else to say
        return nodata
    # the clock of making the chunk
    making = qed.timers.wall("qed.measure.pages.make")
    # make it from its value, the way the library fills a chunk that was never written
    making.reset()
    making.start()
    cell * (len(data) // width)
    making.stop()
    # record the value
    nodata["found"] = interpret(data=cell, cell=dataset.cell.cell, swapped=dataset.cell.byteswap)
    # and the times
    nodata["decode"] = seconds
    nodata["make"] = making.sec()
    # the size of the chunk that holds nothing but this value
    size = min(chunk[1] for chunk in table)
    # every chunk of that size holds the same bytes, since the filters are deterministic
    twins = [chunk for chunk in table if chunk[1] == size]
    # so they are the chunks a declared fill would have spared
    nodata["fillChunks"] = len(twins)
    nodata["fillBytes"] = len(twins) * size
    # check the claim on the first and the last of them in the order of the file
    nodata["verified"] = sum(
        1
        for twin in (min(twins), max(twins))
        if fetch(h5=h5, origin=twin[2], cell=width)[0] == data
    )
    # time what the writer spent on each of them: filtering the chunk at the deflate level
    # that reproduces its stored bytes
    nodata["level"], nodata["encode"] = deflation(
        data=data, stored=size, filters=[entry.name for entry in h5.dcpl.filters], cell=width
    )
    # hand off the record
    return nodata


def deflation(*, data: bytes, stored: int, filters: list, cell: int) -> tuple:
    """
    Find the deflate level at which the chunk {data}, of cells of {cell} bytes, passes
    through {filters} to exactly {stored} bytes, and time that encoding; both are {None}
    when no level does, or when there are filters the encoder does not know
    """
    # the clock
    encoding = qed.timers.wall("qed.measure.pages.encode")
    # go through the levels
    for level in range(1, 10):
        # encode at this one
        encoding.reset()
        encoding.start()
        encoded = encode(data=data, filters=filters, cell=cell, level=level)
        encoding.stop()
        # a pipeline the encoder does not know
        if encoded is None:
            # has no level
            return None, None
        # the level that reproduces the stored size
        if len(encoded) == stored:
            # is the one the writer used
            return level, encoding.sec()
    # no level matched, so the writer used a compressor other than this one
    return None, None


def fetch(*, h5, origin: tuple, cell: int) -> tuple:
    """
    Read the chunk of the dataset {h5} at {origin} as it is stored, and decode it into its
    cells of {cell} bytes, timing the decoding; the data is {None} when the chunk went
    through a filter the decoder does not know
    """
    # read it as it is stored; this fetches the page that holds it
    mask, stored = h5.readChunk(origin=origin)
    # the clock
    decoding = qed.timers.wall("qed.measure.pages.decode")
    # decode it
    decoding.reset()
    decoding.start()
    data = decode(
        stored=stored,
        filters=[entry.name for entry in h5.dcpl.filters],
        mask=mask,
        cell=cell,
    )
    decoding.stop()
    # hand off the cells and the time it took
    return data, decoding.sec()


def attribute(*, h5, name: str):
    """
    The value of the attribute {name} of the dataset {h5} in its own terms, or {None} when it has
    no such attribute
    """
    # a dataset without the attribute
    if not h5.hasAttribute(name):
        # has no value for it
        return None
    # otherwise, read it in its own terms
    return h5.getAttribute(name).value


def histogram(*, values: list) -> list:
    """
    Count {values} between zero and one in {BINS} bins of equal width, with anything at or
    past one in the last bin
    """
    # start with empty bins
    counts = [0] * BINS
    # go through the values
    for value in values:
        # find the bin, keeping the top edge in the last one
        counts[min(int(value * BINS), BINS - 1)] += 1
    # hand off the counts
    return counts


def bars(*, counts: list, width: int = 40) -> list:
    """
    Render the {counts} of a histogram as lines of text, one per bin, with bars scaled to {width}
    """
    # the tallest bin sets the scale
    tallest = max(counts) or 1
    # the share of the range each bin covers, in percent
    step = 100 // len(counts)
    # render each bin
    return [
        f"{step * index:3}-{step * (index + 1):3}%: {'#' * round(width * count / tallest):<{width}} "
        f"{count}"
        for index, count in enumerate(counts)
    ]


# end of file
