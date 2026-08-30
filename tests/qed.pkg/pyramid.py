#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a pyramid level is cell for cell what a strided read of the base would have
produced

This is the invariant the whole pyramid rests on. A zoomed out view costs what it costs
because a strided read of a chunked product decompresses every chunk its footprint covers:
at stride {s} it pays for {s}^2 cells for every cell it keeps. A pyramid removes that by
storing the decimated levels, but only if reading a level is indistinguishable from striding
the base -- otherwise the picture would change depending on whether the level happened to
exist. Decimation is therefore plain striding, exactly what the render kernels do, and
striding composes: halving twice is striding by four
"""

# externals
import os

# support
import journal
import pyre
import qed

# the NISAR fixture this driver reads; part of the shared test data tree
product = pyre.primitives.path(__file__).parent / ".." / "data" / "nisar" / "gslc.h5"
# if it has not been generated
if not product.exists():
    # there is nothing to check
    raise SystemExit(0)

# quiet the configuration chatter
journal.warning("qed.cli").deactivate()

# the h5 bindings
libh5 = qed.h5.libh5

# open the product without measuring it; this driver only moves cells around
reader = qed.readers.nisar.gslc(name="pyramid", uri=f"file:{product}")
reader.open(measure=False)
# take its first dataset as the base of the pyramid
base, *_ = reader.datasets
# its layout
shape = tuple(base.shape)
tile = tuple(base.tile)
# and the in-memory type both levels share
datatype = base.datatype.htype

# the level above the base is half the extent on each axis
extent = [axis // 2 for axis in shape]
# the file that holds it, beside this driver so the suite can clean up after itself
scratch = str(pyre.primitives.path(__file__).parent / "pyramid.h5")
# start from nothing, in case an earlier run left something behind
if os.path.exists(scratch):
    # by removing it
    os.unlink(scratch)

# make the file
cache = libh5.File(scratch, "w")
# the level keeps the chunking of the base, so a tile of it is still one chunk
dcpl = libh5.properties.dcpl()
dcpl.chunk = [min(width, axis) for width, axis in zip(tile, extent)]
# cells nobody writes must read back as fill, and the product is the only authority on
# what its absence looks like, so take the value from it rather than assume one
dcpl.fillValue = base.data.dataset.fillValue
# create the level
level = cache.create(
    path="level1", type=datatype, space=libh5.DataSpace(extent), dcpl=dcpl
)

# the fixture frames its data inside a much larger grid of fill, so a tile taken anywhere
# would likely hold nothing and compare equal for the wrong reason; these destination
# origins have source footprints that land on the data
# they are also exactly the four that feed the level two tile checked below, so the
# composition has a fully populated ancestry
origins = [(16384, 5120), (16384, 5632), (16896, 5120), (16896, 5632)]
# go through them
for origin in origins:
    # build the tile of the level by decimating the base
    qed.libqed.nisar.decimate(
        source=base.data.dataset,
        destination=level,
        datatype=datatype,
        origin=origin,
        shape=tile,
        stride=(2, 2),
    )
    # read the level back at unit stride
    stored = qed.libqed.nisar.sample(
        source=level, datatype=datatype, origin=origin, shape=tile, stride=(1, 1)
    )
    # and read the base the way a client would have, striding by two
    strided = qed.libqed.nisar.sample(
        source=base.data.dataset,
        datatype=datatype,
        origin=origin,
        shape=tile,
        stride=(2, 2),
    )
    # the tile must hold real data, or the comparison proves nothing
    assert stored[0] == tile[0] * tile[1]
    # and the two readings must be indistinguishable
    assert stored == strided

# now build the level above from the level just written, and check that decimation
# composes: striding by two twice must land exactly where striding by four would
second = cache.create(
    path="level2",
    type=datatype,
    space=libh5.DataSpace([axis // 4 for axis in shape]),
    dcpl=dcpl,
)
# take a tile of it whose ancestry runs through the tiles built above
origin = (8192, 2560)
# build it from the level below
qed.libqed.nisar.decimate(
    source=level,
    destination=second,
    datatype=datatype,
    origin=origin,
    shape=tile,
    stride=(2, 2),
)
# read it back at unit stride
stored = qed.libqed.nisar.sample(
    source=second, datatype=datatype, origin=origin, shape=tile, stride=(1, 1)
)
# and read the base the way a client at that zoom would have, striding by four
strided = qed.libqed.nisar.sample(
    source=base.data.dataset, datatype=datatype, origin=origin, shape=tile, stride=(4, 4)
)
# the tile must hold real data, or the comparison proves nothing
assert stored[0] == tile[0] * tile[1]
# and two halvings must be indistinguishable from one quartering
assert stored == strided

# a tile of pure fill is never written, so its chunk stays unallocated; what it reads back
# as is what the level above will see, and it has to be fill. the library's own default is
# zero, which is a perfectly good measurement, and a level built over that default would
# hand the next one a raster with no fill in it at all -- the pyramid would densify one
# level at a time, each holding four times the cells of the one below instead of a quarter
empty = (0, 0)
# decimating a region the product never wrote deposits nothing, and says so
assert (
    qed.libqed.nisar.decimate(
        source=base.data.dataset,
        destination=level,
        datatype=datatype,
        origin=empty,
        shape=tile,
        stride=(2, 2),
    )
    == 0
)
# and reading that region back finds nothing, rather than a field of zeros
assert (
    qed.libqed.nisar.sample(
        source=level, datatype=datatype, origin=empty, shape=tile, stride=(1, 1)
    )[0]
    == 0
)

# close the file before it goes away
cache.close()
# and clean up after the driver
os.unlink(scratch)

# the pyramid of a dataset knows how deep it can go: the top is the level whose whole
# raster fits in a single tile
pyramid = qed.readers.nisar.pyramid(dataset=base, root=scratch + ".d")
# this fixture is large enough to support several halvings
assert pyramid.depth() > 1
# with nothing built, every request falls back to the base at the full stride, which is
# exactly what the reader did before any of this existed
source, stride = pyramid.level(zoom=3)
assert source is base.data.dataset
assert stride == 8
# and the base always serves itself undecimated
source, stride = pyramid.level(zoom=0)
assert source is base.data.dataset
assert stride == 1

# left to itself, a pyramid keeps its levels wherever the workspace says: beside the
# configuration the user launched from, rather than out of sight under a home directory
workspace = qed.workspaces.local(name="pyramid.workspace")
# which is the working directory by default
assert str(workspace.path) == "."
# with the derived data gathered under one folder
assert str(workspace.cache(name="pyramids")) == "./.qed/pyramids"
# and the driver leaves nothing behind
os.rmdir("./.qed/pyramids")
os.rmdir("./.qed")


# end of file
