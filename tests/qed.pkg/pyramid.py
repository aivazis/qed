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
import shutil

# support
import journal
import pyre
import qed

# the product this driver decimates
product = pyre.primitives.path(__file__).parent / ".." / "data" / "nisar" / "gslc.h5"
# a checkout without the fixture has nothing to check
if not product.exists():
    # so bail quietly
    raise SystemExit(0)

# the reader complains about the missing web assets on open; this driver is not the app
journal.warning("qed.cli").deactivate()

# the scratch area for the levels this driver builds
scratch = pyre.primitives.path(__file__).parent / "pyramid.scratch"
# start clean
if scratch.exists():
    # by removing whatever a previous run left behind
    shutil.rmtree(str(scratch))
# and make it
scratch.mkdir()


def occupancy(path, extent, tile, written):
    """
    Write the occupancy record of a level of {extent} diced into {tile}, naming the tiles
    whose origins are in {written}
    """
    # the grid of tiles, edge tiles included
    columns = (extent[1] + tile[1] - 1) // tile[1]
    rows = (extent[0] + tile[0] - 1) // tile[0]
    # nothing written
    record = bytearray(rows * columns)
    # go through the written tiles
    for origin in written:
        # and mark each one, in tile order
        record[(origin[0] // tile[0]) * columns + origin[1] // tile[1]] = 1
    # save it
    with open(str(path), "wb") as stream:
        # in one piece
        stream.write(bytes(record))
    # all done
    return


def level(dataset, name, extent, tile, written, fill):
    """
    Make a level of {extent} diced into {tile} for {dataset} under {name}, ready for writing;
    {written} is the list of tile origins the caller will fill, and the level reads them
    back after the draft is let go
    """
    # the storage classes for cells of this type
    storage = getattr(qed.libqed.pyramid, dataset.datatype.cell)
    # the files
    tiles = str(scratch / f"{name}.tiles")
    record = scratch / f"{name}.occupancy"
    # make the tile file at its full padded size
    storage.Draft.create(tiles=tiles, shape=extent, tile=tile)
    # and the record
    occupancy(path=record, extent=extent, tile=tile, written=written)
    # take hold of the file for writing, and the way a reader would; both map the same
    # file, so a tile written through the one is visible through the other
    draft = storage.Draft(tiles=tiles, shape=extent, tile=tile)
    reader = storage.Level(
        tiles=tiles, occupancy=str(record), shape=extent, tile=tile, fill=fill
    )
    # hand them off
    return draft, reader


# open the product without measuring it; the numbers come out of the decimation
reader = qed.readers.nisar.gslc(name="pyramid", uri=f"file:{product}")
reader.open(measure=False)
# get the base dataset
base, *_ = reader.datasets
# its geometry
shape = tuple(base.shape)
tile = tuple(base.tile)
datatype = base.datatype.htype
# the kernels that read its cells
kernels = base.kernels
# a real product carries a nan for absence
assert base.cell.blank != base.cell.blank

# the first level: half the extent on each axis
extent = tuple(axis // 2 for axis in shape)
# the four tiles this driver fills, a 2x2 block in the middle of the raster
origins = [(16384, 5120), (16384, 5632), (16896, 5120), (16896, 5632)]
# make it
draft, first = level(
    dataset=base,
    name="level1",
    extent=extent,
    tile=tile,
    written=origins,
    fill=base.cell.blank,
)
# go through the tiles
for origin in origins:
    # decimate the base into the level
    deposited = kernels.decimate(
        source=base.data.dataset,
        destination=draft,
        datatype=datatype,
        origin=origin,
        shape=tile,
        stride=(2, 2),
    )
    # what the level holds there
    stored = kernels.sample(
        source=first, datatype=datatype, origin=origin, shape=tile, stride=(1, 1)
    )
    # and what a strided read of the base holds
    strided = kernels.sample(
        source=base.data.dataset,
        datatype=datatype,
        origin=origin,
        shape=tile,
        stride=(2, 2),
    )
    # the tile is full of measurements
    assert stored[0] == tile[0] * tile[1]
    # the level is cell for cell the strided base
    assert stored == strided
    # and the decimation reported exactly what it deposited
    assert deposited == stored

# the second level is built from the first, not from the base: a quarter of the extent
above = tuple(axis // 4 for axis in shape)
# the one tile of it that the block above covers
origin = (8192, 2560)
# make it
draft2, second = level(
    dataset=base,
    name="level2",
    extent=above,
    tile=tile,
    written=[origin],
    fill=base.cell.blank,
)
# decimate the first level into it
kernels.decimate(
    source=first,
    destination=draft2,
    datatype=datatype,
    origin=origin,
    shape=tile,
    stride=(2, 2),
)
# what the second level holds
stored = kernels.sample(
    source=second, datatype=datatype, origin=origin, shape=tile, stride=(1, 1)
)
# is what striding the base by four holds: halving composes
strided = kernels.sample(
    source=base.data.dataset,
    datatype=datatype,
    origin=origin,
    shape=tile,
    stride=(4, 4),
)
assert stored[0] == tile[0] * tile[1]
assert stored == strided

# a tile of pure fill is not written; the corner of this product is empty
empty = (0, 0)
# so the decimation reports nothing deposited
assert (
    kernels.decimate(
        source=base.data.dataset,
        destination=draft,
        datatype=datatype,
        origin=empty,
        shape=tile,
        stride=(2, 2),
    )[0]
    == 0
)
# and the level, whose record does not name that tile, reads fill there
assert (
    kernels.sample(
        source=first, datatype=datatype, origin=empty, shape=tile, stride=(1, 1)
    )[0]
    == 0
)


# a render through the level must be the render off the base
class Stub:
    """
    A pyramid holding the one level this driver built
    """

    def level(self, zoom):
        """
        Serve everything from the level, which owes one halving less than the request
        """
        return first, tuple(step - 1 for step in zoom)


# a tile at zoom one, inside the block this driver decimated
spec = {"zoom": (1, 1), "origin": (16384, 5120), "shape": (256, 256)}
# the amplitude channel
amplitude = base.channel(name="amplitude")
# render off the base
straight = bytes(memoryview(base.render(channel=amplitude, **spec)))
# install the stub
base.pyramid = Stub()
# and render through the level
served = bytes(memoryview(base.render(channel=amplitude, **spec)))
# the two must agree
assert straight == served
# and show something
assert len(set(straight)) > 1
# remove the stub
base.pyramid = None
# and let go of the scratch levels
del draft, draft2, first, second

# the masked renders read a companion raster alongside the data, and both must come from
# the same depth; check that with a covariance product, if the fixture is there
covariances = (
    pyre.primitives.path(__file__).parent / ".." / "data" / "nisar" / "gcov.h5"
)
# if it is
if covariances.exists():
    # open it
    gcov = qed.readers.nisar.gcov(name="pyramid.gcov", uri=f"file:{covariances}")
    gcov.open(measure=False)
    # find the covariance term and its mask
    covariance = [
        entry
        for entry in gcov.datasets
        if dict(entry.selector) == {"band": "L", "frequency": "B", "cov": "HHHH"}
    ][0]
    mask = covariance.mask
    # the covariance is real, the mask is a byte
    assert covariance.datatype.cell == "float32"
    assert mask.datatype.cell == "uint8"
    # the tile this driver checks, at zoom one
    where = {"zoom": (1, 1), "origin": (1024, 1024), "shape": (128, 128)}

    def decimate(dataset, name):
        """
        Halve {dataset} over the footprint of the tile above, and hand back the level
        """
        # the extent of the level and its tile
        extent = tuple(axis // 2 for axis in tuple(dataset.shape))
        chunk = where["shape"]
        # a cell type that cannot say "nothing" fills with what the product declared
        fill = dataset.cell.blank if dataset.cell.blank is not None else 0
        # make the level
        draft, reader = level(
            dataset=dataset,
            name=name,
            extent=extent,
            tile=chunk,
            written=[where["origin"]],
            fill=fill,
        )
        # decimate the one tile
        record = dataset.kernels.decimate(
            source=dataset.data.dataset,
            destination=draft,
            datatype=dataset.datatype.htype,
            origin=where["origin"],
            shape=chunk,
            stride=(2, 2),
        )
        # which held something
        assert record[0] > 0
        # hand back the level
        return reader

    class Stub:
        """
        A pyramid whose only level is the base decimated once
        """

        def __init__(self, level, **kwds):
            # chain up
            super().__init__(**kwds)
            # remember my level
            self.first = level
            # all done
            return

        def level(self, zoom):
            """
            Serve everything from my one level, which owes one halving less than the request
            """
            return self.first, tuple(step - 1 for step in zoom)

        def at(self, exponent):
            """
            Answer the exact request, which i can do at exactly one depth
            """
            return self.first if exponent == 1 else None

    # the masked channel
    channel = covariance.channel(name="covarianceMasked")
    # render off the base
    straight = bytes(memoryview(covariance.render(channel=channel, **where)))
    # which shows something
    assert len(set(straight)) > 1
    # give the data a level but not the mask: the render must fall back to the base for
    # both, since a level and a full resolution mask do not pair
    covariance.pyramid = Stub(level=decimate(dataset=covariance, name="covariance"))
    guarded = bytes(memoryview(covariance.render(channel=channel, **where)))
    assert straight == guarded
    # give the mask its level too: now both come from depth one
    mask.pyramid = Stub(level=decimate(dataset=mask, name="mask"))
    served = bytes(memoryview(covariance.render(channel=channel, **where)))
    assert straight == served
    # the product declares zero as its fill, while framing its data in nans
    assert covariance.data.dataset.fillValue == 0.0
    assert covariance.cell.blank != covariance.cell.blank
    # and a byte mask has no way to say "nothing"
    assert mask.cell.blank is None

    # the pyramid proper: build the first level of the covariance in a scratch workspace
    scratchWorkspace = qed.workspaces.local(name="pyramid.companions.workspace")
    scratchWorkspace.path = str(scratch)
    levels = qed.readers.nisar.pyramid(
        reader=gcov, dataset=covariance, workspace=scratchWorkspace
    )
    levels.build(depth=1)
    # the level exists: its files are there, and so is the sidecar with the statistics
    assert levels.reach() == 1
    assert (levels.home / "level1.tiles").exists()
    assert (levels.home / "level1.occupancy").exists()
    assert levels.sidecar.exists()
    assert levels.statistics.count > 0
    # the corner of the product is empty: the base says so
    corner = {"origin": (0, 0), "shape": (64, 64), "stride": (1, 1)}
    kernels = covariance.kernels
    assert (
        kernels.sample(
            source=covariance.data.dataset, datatype=covariance.datatype.htype, **corner
        )[0]
        == 0
    )
    # and so does the level, whose record does not name that tile
    assert (
        kernels.sample(
            source=levels._levels[1], datatype=covariance.datatype.htype, **corner
        )[0]
        == 0
    )
    # a second pyramid over the same dataset finds the level, and the numbers, on disk
    again = qed.readers.nisar.pyramid(
        reader=gcov, dataset=covariance, workspace=scratchWorkspace
    )
    again.attach()
    assert again.reach() == 1
    assert again.statistics.count == levels.statistics.count
    assert again.statistics.mean == levels.statistics.mean
    # let go
    levels.close()
    again.close()
    covariance.pyramid = None
    mask.pyramid = None

# a pyramid with no levels serves everything off the base, owing the whole zoom
workspace = qed.workspaces.local(name="pyramid.workspace")
pyramid = qed.readers.nisar.pyramid(reader=reader, dataset=base, workspace=workspace)
# the extent supports several halvings
assert pyramid.depth() > 1
# a symmetric request
source, residual = pyramid.level(zoom=(3, 3))
assert source is base.data.dataset
assert residual == (3, 3)
# full resolution
source, residual = pyramid.level(zoom=(0, 0))
assert source is base.data.dataset
assert residual == (0, 0)
# an asymmetric one
source, residual = pyramid.level(zoom=(3, 1))
assert source is base.data.dataset
assert residual == (3, 1)

# the cache is named after the product, not the reader: a second reader of the same file
# under another name lands on the same directory
other = qed.readers.nisar.gslc(name="pyramid.other", uri=f"file:{product}")
other.open(measure=False)
twin, *_ = other.datasets
assert twin.pyre_name != base.pyre_name
assert (
    qed.readers.nisar.pyramid(reader=other, dataset=twin, workspace=workspace).home
    == pyramid.home
)
# the default workspace is the current directory
assert str(workspace.path) == "."
assert str(workspace.cache(name="pyramids")) == "./.qed/pyramids"
assert str(pyramid.home).startswith("./.qed/pyramids/")
# nothing was built there, so the directories are empty
os.rmdir("./.qed/pyramids")
os.rmdir("./.qed")

# a workspace that cannot make its cache says so, and makes nothing
stray = qed.workspaces.local(name="pyramid.stray")
stray.path = "no/such/place"
journal.error("qed.workspace").fatal = False
journal.error("qed.workspace").deactivate()
assert stray.cache(name="pyramids") is None
assert not os.path.exists("no")

# the app owns a workspace
app = qed.shells.qed(name="pyramid.app")
assert isinstance(app.workspace, qed.workspaces.local)

# clean up the scratch area
shutil.rmtree(str(scratch))

# end of file
