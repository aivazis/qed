#! /usr/bin/env python3
# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check how the page occupancy of a dataset is described, on chunk tables small enough to work
out by hand: two datasets share the pages of a file, and a reader that fetches whole pages
moves the bytes of both
"""

# support
import qed

# the page occupancy calculator
occupancy = qed.readers.pages.occupancy

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
