# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise the pyramid bindings: a level written through a draft reads back its tiles and
fill for everything else, and the nisar kernels read a level exactly the way the native
kernels read the same cells in memory
"""

# externals
import math

# the package
import qed
from pyre.extensions.pyre import grid


def tile(cell, rows, columns, values):
    """
    Make a {rows}x{columns} grid of {cell} that holds {values} in row major order
    """
    # make the grid
    g = grid.heap(shape=[rows, columns], cell=cell)
    # go through the values
    for at, value in enumerate(values):
        # and place each one in its cell
        g[divmod(at, columns)] = value
    # all done
    return g


def cells(g):
    """
    Read the cells of the rank 2 grid {g} as a list of rows
    """
    # unpack the extent
    rows, columns = g.shape
    # and collect
    return [[g[row, column] for column in range(columns)] for row in range(rows)]


def pick(rows, origin, shape, stride):
    """
    Gather from {rows} the cells at {origin} and every {stride}-th one after it, {shape} of them
    per axis, with the fill standing in for the ones past the extent
    """
    # the extent of the source
    height, width = len(rows), len(rows[0])
    # the cell at a position, or the fill past the extent
    at = lambda r, c: rows[r][c] if r < height and c < width else fill
    # gather
    return [
        [at(origin[0] + i * stride[0], origin[1] + j * stride[1]) for j in range(shape[1])]
        for i in range(shape[0])
    ]


def same(left, right):
    """
    Check that two lists of rows hold the same cells, counting a pair of nans as equal
    """
    # the rows line up, and so do the cells in each pair of rows
    return len(left) == len(right) and all(
        len(l) == len(r) and all(a == b or (math.isnan(a) and math.isnan(b)) for a, b in zip(l, r))
        for l, r in zip(left, right)
    )


def read(level, origin, shape, stride):
    """
    Read the tile at {origin}+{shape} of {level}, at {stride}, as a list of rows
    """
    # make room for the tile
    destination = grid.heap(shape=list(shape), cell="float32")
    # fill it
    level.read(destination=destination, origin=origin, shape=shape, stride=stride)
    # and hand back its cells
    return cells(destination)


def window(origin, shape):
    """
    Make the dense block of {data} at {origin}+{shape}
    """
    # unpack
    (r0, c0), (rows, columns) = origin, shape
    # gather the values and lay them out
    return tile(
        cell="float32",
        rows=rows,
        columns=columns,
        values=[data(r, c) for r in range(r0, r0 + rows) for c in range(c0, c0 + columns)],
    )


# the pair of classes over single precision reals
storage = qed.libqed.pyramid.float32
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
tile_ = (3, 4)
# the fill
fill = float("nan")


# what a written cell carries: rows in the hundreds, columns in the units
def data(r, c):
    """
    The value of the cell at ({r}, {c})
    """
    # rows in the hundreds, columns in the units
    return float(100 * r + c)


# make the file at its full padded size
storage.Draft.create(tiles=tiles, shape=shape, tile=tile_)
# take hold of it for writing
draft = storage.Draft(tiles=tiles, shape=shape, tile=tile_)
# the layout must be what we asked for
assert draft.shape == shape
assert draft.tile == tile_
assert draft.tiles == (3, 3)
# write the interior tile at the origin
draft.write(origin=(0, 0), data=window(origin=(0, 0), shape=(3, 4)))
# the edge tile in the middle row, clipped to the extent
draft.write(origin=(3, 8), data=window(origin=(3, 8), shape=(3, 1)))
# the edge tile in the last row, clipped to the extent
draft.write(origin=(6, 4), data=window(origin=(6, 4), shape=(1, 4)))
# a buffer of the wrong cell type is refused
try:
    draft.write(origin=(0, 0), data=grid.heap(shape=[3, 4], cell="float64"))
except ValueError:
    pass
else:
    raise AssertionError("a float64 buffer was accepted by a float32 draft")
# name the tiles that were written, in tile order
with open(occupancy, "wb") as record:
    record.write(bytes([1, 0, 0, 0, 0, 1, 0, 1, 0]))

# what a reader should see: the written tiles, and fill everywhere else
written = [((0, 0), (3, 4)), ((3, 8), (3, 1)), ((6, 4), (1, 4))]
expected = [
    [
        (
            data(r, c)
            if any(o[0] <= r < o[0] + s[0] and o[1] <= c < o[1] + s[1] for o, s in written)
            else fill
        )
        for c in range(shape[1])
    ]
    for r in range(shape[0])
]

# take hold of the level for reading
level = storage.Level(tiles=tiles, occupancy=occupancy, shape=shape, tile=tile_, fill=fill)
# the layout must match
assert level.shape == shape
assert level.tile == tile_
assert level.tiles == (3, 3)
assert math.isnan(level.fill)
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
assert same(read(level, origin=(0, 0), shape=shape, stride=(1, 1)), expected)
# a strided read from the origin: every other cell along both axes
assert same(
    read(level, origin=(0, 0), shape=(4, 5), stride=(2, 2)),
    pick(expected, origin=(0, 0), shape=(4, 5), stride=(2, 2)),
)
# a strided read away from the origin, with different strides on the two axes
assert same(
    read(level, origin=(3, 4), shape=(2, 2), stride=(3, 4)),
    pick(expected, origin=(3, 4), shape=(2, 2), stride=(3, 4)),
)
# a read whose footprint runs past the extent gets fill for the overhang
assert same(
    read(level, origin=(3, 6), shape=(5, 4), stride=(3, 3)),
    pick(expected, origin=(3, 6), shape=(5, 4), stride=(3, 3)),
)
# a destination of the wrong shape is refused
try:
    level.read(
        destination=grid.heap(shape=[2, 2], cell="float32"),
        origin=(0, 0),
        shape=(3, 3),
        stride=(1, 1),
    )
except ValueError:
    pass
else:
    raise AssertionError("a 2x2 destination was accepted for a 3x3 tile")

# the cells of every other row and column, as a dense grid of their own
decimated = pick(expected, origin=(0, 0), shape=(4, 5), stride=(2, 2))
reference = tile(
    cell="float32", rows=4, columns=5, values=[cell for row in decimated for cell in row]
)
# the sample kernel over the level must agree with the native one over the cells
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
storage.Draft.create(tiles=above, shape=aboveShape, tile=tile_)
# take hold of it
draftAbove = storage.Draft(tiles=above, shape=aboveShape, tile=tile_)
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
levelAbove = storage.Level(
    tiles=above, occupancy=aboveOccupancy, shape=aboveShape, tile=tile_, fill=fill
)
assert same(
    read(levelAbove, origin=(0, 0), shape=aboveShape, stride=(1, 1)),
    pick(decimated, origin=(0, 0), shape=aboveShape, stride=(1, 1)),
)


# end of file
