# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved

"""
Exercise the pyramid bindings: a level written through a draft reads back its tiles and
fill for everything else, and the nisar kernels read a level exactly the way the native
kernels read the same cells in memory
"""

# support
import os

# externals
import numpy as np

# the package
import qed

# the pair of classes over single precision reals
cells = qed.libqed.pyramid.float32
# the kernels over the same cells
kernels = qed.libqed.nisar.cells.float32
# the memory type the hdf5 path would convert to; a level has no use for it, but the
# kernels ask for one either way
datatype = qed.h5.memtypes.float32.htype

# the files
tiles = "pyramid.tiles"
occupancy = "pyramid.occupancy"
# a level of 7x9 cells diced into 3x4 tiles: a 3x3 grid of tiles, with padding on both
# trailing edges
shape = (7, 9)
tile = (3, 4)
# the fill
fill = float("nan")

# what a written cell carries: rows in the hundreds, columns in the units
data = np.fromfunction(lambda r, c: 100 * r + c, shape, dtype=np.float32)

# make the file at its full padded size
cells.Draft.create(tiles=tiles, shape=shape, tile=tile)
# take hold of it for writing
draft = cells.Draft(tiles=tiles, shape=shape, tile=tile)
# the layout must be what we asked for
assert draft.shape == shape
assert draft.tile == tile
assert draft.tiles == (3, 3)
# write the interior tile at the origin
draft.write(origin=(0, 0), data=np.ascontiguousarray(data[0:3, 0:4]))
# the edge tile in the middle row, clipped to the extent
draft.write(origin=(3, 8), data=np.ascontiguousarray(data[3:6, 8:9]))
# the edge tile in the last row, clipped to the extent
draft.write(origin=(6, 4), data=np.ascontiguousarray(data[6:7, 4:8]))
# a buffer of the wrong cell type is refused
try:
    draft.write(origin=(0, 0), data=np.zeros((3, 4), dtype=np.float64))
except ValueError:
    pass
else:
    raise AssertionError("a float64 buffer was accepted by a float32 draft")
# name the tiles that were written, in tile order
with open(occupancy, "wb") as record:
    record.write(bytes([1, 0, 0, 0, 0, 1, 0, 1, 0]))

# what a reader should see: the written tiles, and fill everywhere else
expected = np.full(shape, fill, dtype=np.float32)
expected[0:3, 0:4] = data[0:3, 0:4]
expected[3:6, 8:9] = data[3:6, 8:9]
expected[6:7, 4:8] = data[6:7, 4:8]

# take hold of the level for reading
level = cells.Level(tiles=tiles, occupancy=occupancy, shape=shape, tile=tile, fill=fill)
# the layout must match
assert level.shape == shape
assert level.tile == tile
assert level.tiles == (3, 3)
assert np.isnan(level.fill)
# the occupancy record must be honored
assert level.occupied(tile=(0, 0))
assert level.occupied(tile=(1, 2))
assert level.occupied(tile=(2, 1))
assert not level.occupied(tile=(1, 1))
# a cell in a written tile is held, one outside the extent is not
assert level.holds(cell=(5, 8))
assert not level.holds(cell=(3, 9))
assert not level.holds(cell=(0, 4))

# read the whole level at unit stride
whole = level.read(origin=(0, 0), shape=shape, stride=(1, 1))
assert whole.dtype == np.float32
assert np.array_equal(whole, expected, equal_nan=True)
# a strided read from the origin: every other cell along both axes
strided = level.read(origin=(0, 0), shape=(4, 5), stride=(2, 2))
assert np.array_equal(strided, expected[::2, ::2], equal_nan=True)
# a strided read away from the origin, with different strides on the two axes
offset = level.read(origin=(3, 4), shape=(2, 2), stride=(3, 4))
assert np.array_equal(offset, expected[3::3, 4::4][:2, :2], equal_nan=True)
# a read whose footprint runs past the extent gets fill for the overhang
overhang = level.read(origin=(3, 6), shape=(5, 4), stride=(3, 3))
assert overhang.shape == (5, 4)
assert np.array_equal(overhang[:2, :1], expected[3::3, 6::3][:2, :1], equal_nan=True)
assert np.all(np.isnan(overhang[2:, :]))
assert np.all(np.isnan(overhang[:, 1:]))

# the sample kernel over the level must agree with the native one over the cells
reference = np.ascontiguousarray(expected[::2, ::2])
record = kernels.sample(source=level, datatype=datatype, origin=(0, 0), shape=(4, 5), stride=(2, 2))
native = qed.libqed.native.sample(source=reference, origin=(0, 0), shape=(4, 5), stride=(1, 1))
assert record == native
# and so must a render
bmp = qed.libqed.nisar.real.value(
    source=level,
    datatype=datatype,
    origin=(0, 0),
    shape=(4, 5),
    stride=(2, 2),
    min=0.0,
    max=608.0,
)
native = qed.libqed.native.channels.value(
    source=reference, origin=(0, 0), shape=(4, 5), stride=(1, 1), min=0.0, max=608.0
)
assert memoryview(bmp).tobytes() == memoryview(native).tobytes()

# the next level up is built by decimating this one into a draft
above = "above.tiles"
aboveOccupancy = "above.occupancy"
# half the extent on each axis
aboveShape = (3, 4)
# make the file
cells.Draft.create(tiles=above, shape=aboveShape, tile=tile)
# take hold of it
draftAbove = cells.Draft(tiles=above, shape=aboveShape, tile=tile)
# and decimate the level into its one tile
record = kernels.decimate(
    source=level,
    destination=draftAbove,
    datatype=datatype,
    origin=(0, 0),
    shape=aboveShape,
    stride=(2, 2),
)
# the record describes the cells that were moved
native = qed.libqed.native.sample(source=reference, origin=(0, 0), shape=aboveShape, stride=(1, 1))
assert record == native
# the tile held something, so it was written
with open(aboveOccupancy, "wb") as record:
    record.write(bytes([1]))
# read it back
levelAbove = cells.Level(
    tiles=above, occupancy=aboveOccupancy, shape=aboveShape, tile=tile, fill=fill
)
assert np.array_equal(
    levelAbove.read(origin=(0, 0), shape=aboveShape, stride=(1, 1)),
    expected[::2, ::2][:3, :4],
    equal_nan=True,
)

# clean up
for name in (tiles, occupancy, above, aboveOccupancy):
    os.remove(name)

# end of file
