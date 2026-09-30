#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check the description of how a raster sits in its file, on the NISAR GCOV fixture, which is
written the way the GCOV writer does it: the library is told the fill is zero, the rasters use
nan, and the chunks that hold nothing but nan are written anyway
"""

# externals
import collections
import math

# support
import journal
import pyre
import qed

# the graphql description of a layout
from qed.gql.layout.Layout import Layout

# the NISAR fixture this driver reads; part of the shared test data tree
product = pyre.primitives.path(__file__).parent / ".." / "data" / "nisar" / "gcov.h5"
# if it has not been generated
if not product.exists():
    # there is nothing to check
    raise SystemExit(0)

# quiet the configuration chatter
journal.warning("qed.cli").deactivate()

# open the product
reader = qed.readers.nisar.gcov(name="layout", uri=f"file:{product}")
reader.open(measure=False)
# the page layout of its file
paging = qed.readers.pages.paging(reader=reader)
# and the storage of every dataset in it
tables = qed.readers.pages.tables(reader=reader)

# the file is paged
pageSize, strategy, size = paging
assert strategy == "page" and pageSize > 0 and size > 0
# and the storage covers the datasets the reader does not display, under their paths
assert any(name.startswith("/") for name in tables)

# a covariance term and the mask of the smaller frequency
term, mask = (
    next(dataset for dataset in reader.datasets if dataset.pyre_name.endswith(suffix))
    for suffix in ("L.B.HHHH", "L.B.mask")
)

# describe the covariance term
described = qed.readers.pages.describe(dataset=term, tables=tables, paging=paging)
# its storage settings
storage = described["storage"]
assert storage["tile"] == (512, 512)
assert storage["filters"] == ["shuffle", "deflate"]
# every cell of its chunk grid was written
record = described["record"]
assert record["written"] == record["grid"]
# the library was never told the fill, so it hands out its default of zero
fill = described["nodata"]
assert fill["status"] == "default" and fill["hdf5"] == 0.0
# while the attribute declares nan, and the empty chunks hold it
assert math.isnan(fill["cf"]) and math.isnan(fill["found"])
# the grid of states covers every chunk
grid = described["states"]
assert grid["rows"] * grid["cols"] == record["grid"]
# none of them unwritten, since the writer cannot leave any out
states = collections.Counter(qed.readers.pages.STATES[code] for code in grid["codes"])
assert states["unwritten"] == 0
# the chunks of fill in the grid are the ones the fill check counted
assert states["fill"] == fill["fillChunks"] > 0
# and the chunks of fill were checked by decoding two of them
assert fill["verified"] == 2

# the map of the file covers every one of its pages
filemap = described["filemap"]
assert filemap["pages"] == -(-size // pageSize)
# with every raster of the product, and the covariance term among them
rasters = filemap["rasters"]
assert len(rasters) == len(reader.datasets)
assert rasters[filemap["selected"]]["name"] == term.pyre_name
# each raster accounts for every byte and every chunk it stores
for raster in rasters:
    # its bytes
    assert sum(raster["bytes"]) == sum(size for _, size, _ in tables[raster["name"]])
    # and its chunks, each counted at least once
    assert sum(raster["chunks"]) >= len(tables[raster["name"]])
# the datasets the product does not display account for the rest of the stored bytes
assert sum(filemap["others"]) == sum(
    size for name, table in tables.items() if name.startswith("/") for _, size, _ in table
)
# no page holds more than it can
for page in range(filemap["pages"]):
    # counting the rasters and everybody else
    assert filemap["others"][page] + sum(raster["bytes"][page] for raster in rasters) <= pageSize
# which the graphql view hands over as is
assert Layout.resolve_filemap(described) is filemap

# the graphql view of the fill says the two disagree
view = Layout.resolve_fill(described)
assert view["hdf5"] == "0.0" and view["holds"] == "nan" and view["agrees"] is False
# and the grid carries the names of the states
assert Layout.resolve_grid(described)["states"] == list(qed.readers.pages.STATES)

# the measures of the raster, by the names the census gives them, cover every measure of a census
mine = qed.measurements.census.measures(description=described)
assert {name for name, _, _ in qed.measurements.census.MEASURES} <= set(mine)
# and agree with the description
assert mine["fill_chunks"] == fill["fillChunks"]
assert mine["unwritten"] == 0

# the mask uses 255 for the places outside the swath, which the library does not know either
fill = qed.readers.pages.describe(dataset=mask, tables=tables, paging=paging)["nodata"]
assert fill["hdf5"] == 0 and fill["cf"] == 255 and fill["found"] == 255


# end of file
