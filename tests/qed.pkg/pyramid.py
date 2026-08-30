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
# create the level
level = cache.create(
    path="level1", type=datatype, space=libh5.DataSpace(extent), dcpl=dcpl
)

# the fixture frames its data inside a much larger grid of fill, so a tile taken anywhere
# would likely hold nothing and compare equal for the wrong reason; these destination
# origins have source footprints that land on the data
origins = [(14336, 4608), (16384, 5120), (15360, 5632)]
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

# close the file before it goes away
cache.close()
# and clean up after the driver
os.unlink(scratch)


# end of file
