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
# a raster is read into a buffer of its own cells, so the kernels come from the dataset
# rather than from a fixed instantiation that happens to suit one product
kernels = base.kernels

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
    deposited = kernels.decimate(
        source=base.data.dataset,
        destination=level,
        datatype=datatype,
        origin=origin,
        shape=tile,
        stride=(2, 2),
    )
    # read the level back at unit stride
    stored = kernels.sample(
        source=level, datatype=datatype, origin=origin, shape=tile, stride=(1, 1)
    )
    # and read the base the way a client would have, striding by two
    strided = kernels.sample(
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
    # the decimation measured the very cells it moved, so its own record agrees with both
    # without anybody reading them a second time
    assert deposited == stored

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
kernels.decimate(
    source=level,
    destination=second,
    datatype=datatype,
    origin=origin,
    shape=tile,
    stride=(2, 2),
)
# read it back at unit stride
stored = kernels.sample(
    source=second, datatype=datatype, origin=origin, shape=tile, stride=(1, 1)
)
# and read the base the way a client at that zoom would have, striding by four
strided = kernels.sample(
    source=base.data.dataset,
    datatype=datatype,
    origin=origin,
    shape=tile,
    stride=(4, 4),
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
# decimating a region the product never wrote deposits nothing, and says so: the record it
# reports counts no cells at all
assert (
    kernels.decimate(
        source=base.data.dataset,
        destination=level,
        datatype=datatype,
        origin=empty,
        shape=tile,
        stride=(2, 2),
    )[0]
    == 0
)
# and reading that region back finds nothing, rather than a field of zeros
assert (
    kernels.sample(
        source=level, datatype=datatype, origin=empty, shape=tile, stride=(1, 1)
    )[0]
    == 0
)


# the point of the whole exercise: a render served from a level must be the same picture
# as one that strides the base. stand in for a pyramid with the level built above, which
# covers the tiles this render reads
class Stub:
    """
    A pyramid holding the one level this driver built
    """

    # interface
    def level(self, zoom):
        """
        Serve everything from the level, which owes one halving less than the request
        """
        # the level is the base decimated once, so it owes whatever is left
        return level, tuple(step - 1 for step in zoom)


# a tile whose footprint lies inside the level tiles built above
spec = {"zoom": (1, 1), "origin": (16384, 5120), "shape": (256, 256)}
# the channel that renders it
amplitude = base.channel(name="amplitude")
# render it the way the reader always has, striding the product
straight = bytes(memoryview(base.render(channel=amplitude, **spec)))
# hand the dataset its levels and render again
base.pyramid = Stub()
served = bytes(memoryview(base.render(channel=amplitude, **spec)))
# the pictures must be indistinguishable, or the pyramid would change what a user sees
# depending on whether it happened to have been built
assert straight == served
# and the tile must hold something, or the comparison proves nothing
assert len(set(straight)) > 1
# put the dataset back the way it was
base.pyramid = None

# a render that reads a companion raster alongside its data -- a mask -- reads both with one
# origin and one stride, so the two have to come from the same depth. this is where a
# covariance term, whose cells are real and whose mask is a single byte per cell, exercises
# both halves of that: the levels of the two rasters are built by different kernels, and the
# render must pair them correctly or refuse the level altogether
covariances = (
    pyre.primitives.path(__file__).parent / ".." / "data" / "nisar" / "gcov.h5"
)
# when that fixture has been generated
if covariances.exists():
    # open it
    gcov = qed.readers.nisar.gcov(name="pyramid.gcov", uri=f"file:{covariances}")
    gcov.open(measure=False)
    # take a covariance term of the smaller frequency, which carries a mask alongside its
    # data; it is the same arrangement as the larger one and there is less of it to decimate
    covariance = [
        entry
        for entry in gcov.datasets
        if dict(entry.selector) == {"band": "L", "frequency": "B", "cov": "HHHH"}
    ][0]
    # and the mask it is read with
    mask = covariance.mask

    # the two rasters hold different kinds of number, so each is decimated by the kernels
    # of its own cell type; reading either into a buffer laid out for the other would
    # deposit pairs, or halves, of what the file actually holds
    assert covariance.datatype.cell == "float32"
    assert mask.datatype.cell == "uint8"

    # the tile to draw, one halving out
    where = {"zoom": (1, 1), "origin": (1024, 1024), "shape": (128, 128)}
    # a file to keep the levels of both rasters in
    derived = str(pyre.primitives.path(__file__).parent / "companions.h5")
    # starting from nothing, in case an earlier run left something behind
    if os.path.exists(derived):
        # by removing it
        os.unlink(derived)
    # make it
    store = libh5.File(derived, "w")

    # build the first level of one raster over the region the render will read
    def decimate(dataset, name):
        """
        Halve {dataset} over the footprint of the tile above, and hand back the level
        """
        # the level covers the whole raster, halved on each axis
        extent = [axis // 2 for axis in tuple(dataset.shape)]
        # lay it out in chunks the size of the tile being drawn
        plan = libh5.properties.dcpl()
        plan.chunk = list(where["shape"])
        # spelling absence exactly the way the raster it comes from does
        plan.fillValue = dataset.data.dataset.fillValue
        # make it
        target = store.create(
            path=name,
            type=dataset.datatype.htype,
            space=libh5.DataSpace(extent),
            dcpl=plan,
        )
        # fill the one tile the render will ask for, with the kernels of its own cell type
        record = dataset.kernels.decimate(
            source=dataset.data.dataset,
            destination=target,
            datatype=dataset.datatype.htype,
            origin=where["origin"],
            shape=where["shape"],
            stride=(2, 2),
        )
        # the region has to hold data, or none of the comparisons below prove anything
        assert record[0] > 0
        # hand off the level
        return target

    # a pyramid holding the single level built for one raster
    class Stub:
        """
        A pyramid whose only level is the base decimated once
        """

        # metamethods
        def __init__(self, level, **kwds):
            # chain up
            super().__init__(**kwds)
            # remember the level i hold
            self.first = level
            # all done
            return

        # interface
        def level(self, zoom):
            """
            Serve everything from my one level, which owes one halving less than the request
            """
            # the level is the base decimated once, so it owes whatever is left
            return self.first, tuple(step - 1 for step in zoom)

        def at(self, exponent):
            """
            Answer the exact request, which i can do at exactly one depth
            """
            # i hold the first level and nothing else
            return self.first if exponent == 1 else None

    # render the masked channel the way the reader always has, striding the product
    channel = covariance.channel(name="covarianceMasked")
    straight = bytes(memoryview(covariance.render(channel=channel, **where)))
    # the picture has to have some structure in it, or comparing it proves nothing
    assert len(set(straight)) > 1

    # now offer the data a level while the mask has none. the render must decline it: a
    # level for one raster and the product for the other would pair every data cell with
    # the mask value of a cell half the distance away
    covariance.pyramid = Stub(level=decimate(dataset=covariance, name="data"))
    guarded = bytes(memoryview(covariance.render(channel=channel, **where)))
    # so the picture is unchanged
    assert straight == guarded

    # give the mask its own level, at the same depth and built by its own kernels
    mask.pyramid = Stub(level=decimate(dataset=mask, name="mask"))
    served = bytes(memoryview(covariance.render(channel=channel, **where)))
    # now the render can take both from their levels, and the picture is still the one the
    # product would have given: a level is cell for cell what striding the base produces
    assert straight == served

    # put the datasets back the way they were and let the file go
    covariance.pyramid = None
    mask.pyramid = None
    store.close()
    os.unlink(derived)

# close the file before it goes away
cache.close()
# and clean up after the driver
os.unlink(scratch)

# a pyramid is told where it lives rather than going looking: the workspace the
# application owns is the one authority on where derived data goes
workspace = qed.workspaces.local(name="pyramid.workspace")
# the pyramid of a dataset knows how deep it can go: the top is the level whose whole
# raster fits in a single tile
pyramid = qed.readers.nisar.pyramid(reader=reader, dataset=base, workspace=workspace)
# this fixture is large enough to support several halvings
assert pyramid.depth() > 1
# with nothing built, every request falls back to the base at the full stride, which is
# exactly what the reader did before any of this existed
source, residual = pyramid.level(zoom=(3, 3))
assert source is base.data.dataset
assert residual == (3, 3)
# and a request at full resolution owes nothing
source, residual = pyramid.level(zoom=(0, 0))
assert source is base.data.dataset
assert residual == (0, 0)
# the two axes are not required to agree, since the client can decouple them; a request
# that zooms one axis further than the other is served by the level that over-decimates
# neither, and each axis makes up its own difference by striding what it reads
source, residual = pyramid.level(zoom=(3, 1))
assert source is base.data.dataset
assert residual == (3, 1)

# a cache is written by one process and read by others -- a crew member calls the same
# reader something else, and a later run may call it a third thing -- so the names inside
# it must come from the product rather than from whatever this process named its reader
other = qed.readers.nisar.gslc(name="pyramid.other", uri=f"file:{product}")
other.open(measure=False)
twin, *_ = other.datasets
# the two readers disagree about what to call themselves
assert twin.pyre_name != base.pyre_name
# but their pyramids agree on where everything goes
assert (
    qed.readers.nisar.pyramid(reader=other, dataset=twin, workspace=workspace).path
    == pyramid.path
)

# the workspace keeps derived data beside the configuration the user launched from,
# rather than out of sight under a home directory
assert str(workspace.path) == "."
# gathered under one folder
assert str(workspace.cache(name="pyramids")) == "./.qed/pyramids"
# which is where the pyramid puts its levels
assert str(pyramid.path).startswith("./.qed/pyramids/")
# and the driver leaves nothing behind
os.rmdir("./.qed/pyramids")
os.rmdir("./.qed")

# the workspace directory belongs to the user; a workspace pointed at one that does not
# exist says so rather than making it, since making it silently would turn a typo in the
# configuration into a tree of empty directories
stray = qed.workspaces.local(name="pyramid.stray")
stray.path = "no/such/place"
# the complaint is the point, so let it out where a human would see it, but not here
journal.error("qed.workspace").fatal = False
journal.error("qed.workspace").deactivate()
# there is nowhere to keep anything
assert stray.cache(name="pyramids") is None
# and nothing was made on the way to finding that out
assert not os.path.exists("no")

# the application owns the workspace, so everything that derives anything can be pointed
# at the same one
app = qed.shells.qed(name="pyramid.app")
# it resolves to the local flavor by default
assert isinstance(app.workspace, qed.workspaces.local)


# end of file
