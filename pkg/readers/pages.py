# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import collections
import statistics

# the share of its raw size below which a written chunk counts as nearly empty: such a chunk
# holds almost nothing but the fill value, and costs a reader as much as a full one
NEARLY_EMPTY = 0.01
# the number of bins of the histograms, each covering an equal share of the range
BINS = 10


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
