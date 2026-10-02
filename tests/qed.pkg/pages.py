#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check how the page occupancy of a dataset is described, on chunk tables small enough to work
out by hand: two datasets share the pages of a file, and a reader that fetches whole pages
moves the bytes of both
"""

# externals
import math
import struct
import sys
import zlib

# support
import qed

# the page analyses
pages = qed.readers.pages
# and the page occupancy calculator among them
occupancy = pages.occupancy

# pages of 100 bytes, chunks of 2x2 cells that are 50 bytes before compression; dataset {a}
# has two chunks on the first page, with a chunk of {b} between them, and two on the second
tables = {
    "a": [(0, 30, (0, 0)), (60, 30, (0, 2)), (100, 45, (2, 0)), (145, 45, (2, 2))],
    "b": [(30, 30, (0, 0))],
}
# describe {a}
record = occupancy(tables=tables, name="a", pageSize=100, raw=50, tile=(2, 2), grid=4)

# every chunk of the grid was written, and none of them is nearly empty
assert record["written"] == 4
assert record["empty"] == 0
# the chunks store 150 of the 200 bytes they hold
assert record["stored"] == 150
assert abs(record["compression"] - 200 / 150) < 1e-12
# their sizes, as shares of the raw size, fall in the bins of 60% and 90%
assert record["sizes"] == [0, 0, 0, 0, 0, 0, 2, 0, 0, 2]
# each chunk lies on one of two pages
assert record["pages"] == 2
assert record["spans"] == {1: 4}
# reading the chunks one at a time fetches a page for each of them
assert abs(record["alone"] - 400 / 150) < 1e-12
# reading them all with each page fetched once fetches the two pages
assert abs(record["once"] - 200 / 150) < 1e-12
# {b} shares the first page
assert record["partners"] == {"b": 30}
# and reading both fetches the same two pages for 180 bytes
assert abs(record["joint"] - 200 / 180) < 1e-12
# {a} fills 60% of the first page and 90% of the second
assert abs(record["fillMedian"] - 0.75) < 1e-12
assert abs(record["fillMean"] - 0.75) < 1e-12
assert record["fillFull"] == 0.5
# both datasets together fill 90% of each
assert abs(record["totalMean"] - 0.9) < 1e-12
# three chunks touch the first page and two the second
assert record["tenants"] == 2.5
# the chunks that follow each other on a page are neighbors on the raster
assert record["locality"] == 1.0

# a dataset whose chunks share pages with chunks from across the raster has no locality
scattered = {"c": [(0, 40, (0, 0)), (40, 40, (8, 8))]}
# describe it
record = occupancy(tables=scattered, name="c", pageSize=100, raw=50, tile=(2, 2), grid=25)
# the two chunks are on the same page but not neighbors
assert record["locality"] == 0.0
# and they have the page to themselves
assert record["partners"] == {}
assert abs(record["joint"] - record["once"]) < 1e-12

# a chunk that stores next to nothing counts as nearly empty
sparse = {"d": [(0, 0, (0, 0)), (1, 50, (0, 2))]}
# describe it
record = occupancy(tables=sparse, name="d", pageSize=100, raw=50, tile=(2, 2), grid=4)
# one of its two chunks is nearly empty
assert record["empty"] == 1

# a nearly empty chunk alone on a page costs a page of its own
lonely = {"e": [(0, 500, (0, 0)), (100, 5, (0, 2))]}
# describe it
record = occupancy(tables=lonely, name="e", pageSize=100, raw=1000, tile=(2, 2), grid=4)
# one of its chunks is nearly empty, and stores five bytes
assert record["empty"] == 1
assert record["emptyStored"] == 5
# the other spans pages 0 through 4, so the empty one has page 1 to share with it
assert record["emptyPages"] == 0
# but moved past the end of the other, it has a page to itself
lonely = {"e": [(0, 500, (0, 0)), (500, 5, (0, 2))]}
# describe it
record = occupancy(tables=lonely, name="e", pageSize=100, raw=1000, tile=(2, 2), grid=4)
# and a reader fetches that page for nothing else
assert record["emptyPages"] == 1

# a chunk of four cells of four bytes each, as a writer that declares no fill would store it
cells = struct.pack("<4f", *([math.nan] * 4))
# shuffled: byte k of every cell in plane k
shuffled = bytes(cells[k + 4 * i] for k in range(4) for i in range(4))
# and deflated
stored = zlib.compress(shuffled)
# decoding undoes both
decoded = pages.decode(stored=stored, filters=["shuffle", "deflate"], mask=0, cell=4)
assert decoded == cells
# encoding shuffles and deflates, which reproduces the stored bytes at the level they were made
assert pages.shuffle(data=cells, cell=4) == shuffled
assert pages.encode(data=cells, filters=["shuffle", "deflate"], cell=4, level=6) == stored
# and a filter the encoder does not know stops it
assert pages.encode(data=cells, filters=["szip"], cell=4, level=6) is None
# a filter the library skipped, as the mask says, is not undone
assert pages.decode(stored=shuffled, filters=["shuffle", "deflate"], mask=0b10, cell=4) == cells
# a filter the decoder does not know stops it
assert pages.decode(stored=stored, filters=["szip"], mask=0, cell=4) is None
# the chunk repeats one cell
cell = pages.uniform(data=decoded, cell=4)
assert cell == cells[:4]
# which is a nan
assert math.isnan(pages.interpret(data=cell, cell="float32"))
# a chunk with different cells repeats none
assert pages.uniform(data=struct.pack("<4f", 1, 2, 3, 4), cell=4) is None
# a complex cell is a pair of parts
assert pages.interpret(data=struct.pack("<2f", 1, -2), cell="complex64") == complex(1, -2)
# and a cell in the order the host lacks is swapped back
assert pages.interpret(data=b"\x01\x00", cell="uint16", swapped=sys.byteorder == "big") == 1

# the states of a grid of two by three chunks of 2x2 cells, over a raster of 4x5 cells: one chunk
# of fill, one sliver, two of data, and two never written
grid = pages.states(
    table=[(0, 5, (0, 0)), (5, 7, (0, 2)), (12, 40, (2, 0)), (52, 45, (2, 4))],
    shape=(4, 5),
    tile=(2, 2),
    raw=1000,
    fill=5,
)
# the grid is two by three
assert (grid["rows"], grid["cols"]) == (2, 3)
# with the states in row major order
assert [pages.STATES[code] for code in grid["codes"]] == [
    "fill",
    "sliver",
    "unwritten",
    "data",
    "unwritten",
    "data",
]
# and the sizes of the chunks, zero where there are none
assert grid["sizes"] == [5, 7, 0, 40, 0, 45]
# without pages, no chunk starts on one
assert grid["pages"] == [-1] * 6

# the strip of the pages of {a}, which shares its first page with {b}
described = pages.strip(tables=tables, name="a", pageSize=100)
# it lands on two pages
assert described["pages"] == [0, 1]
# with 60 of its bytes and two chunks on the first, and 90 bytes and two chunks on the second
assert described["mine"] == [60, 90] and described["chunks"] == [2, 2]
# {b} has 30 bytes on the first, and nobody else is on the second
assert described["others"] == [30, 0]
assert described["partner"] == ["b", ""] and described["partnerBytes"] == [30, 0]
# a file without pages has no strip
assert pages.strip(tables=tables, name="a", pageSize=0) is None
# and the chunks of {a} start on the pages their addresses fall in
assert pages.states(table=tables["a"], shape=(4, 4), tile=(2, 2), raw=50, pageSize=100)[
    "pages"
] == [0, 0, 1, 1]

# a file without pages describes the chunks and nothing else
record = occupancy(tables=tables, name="a", pageSize=0, raw=50, tile=(2, 2), grid=4)
# the chunk table is there
assert record["written"] == 4
# but the page description is not
assert "pages" not in record

# the histogram rendering has one line per bin, with the tallest bin at full width
lines = qed.readers.pages.bars(counts=[0, 2, 1, 0, 0, 0, 0, 0, 0, 0], width=4)
# one per bin
assert len(lines) == 10
# the tallest bin at full width
assert lines[1] == " 10- 20%: #### 2"
# and half of it for a bin half as tall
assert lines[2] == " 20- 30%: ##   1"


# end of file
