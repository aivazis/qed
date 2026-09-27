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

# the share of its raw size below which a written chunk counts as nearly empty: such a chunk
# holds almost nothing but the fill value, and costs a reader as much as a full one
NEARLY_EMPTY = 0.01
# the number of bins of the histograms, each covering an equal share of the range
BINS = 10
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
        # has no value i can tell
        return None
    # the byte order: the host's, unless swapped
    order = "<" if (sys.byteorder == "little") != swapped else ">"
    # unpack the parts
    parts = struct.unpack(order + layout, data)
    # a pair of parts is a complex number, and a lone part is the value
    return complex(*parts) if len(parts) == 2 else parts[0]


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
