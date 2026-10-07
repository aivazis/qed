#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Render tiles of the value of a real raster through the flow pipeline and through the iterators,
and check that the two encode the same bytes: for every cell type the dispatcher holds, for tiles
that are square and tiles that are not, whose lines need padding, decimated or not, and as the
interval changes from one tile to the next
"""

# support
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


# the kernels
native = qed.libqed.native

# the extent of the raster
rows, columns = 37, 53

# the cell types, as pyre names them, and the values each one can hold
types = {
    "int8": lambda i: i % 120 - 60,
    "uint8": lambda i: i % 250,
    "int16": lambda i: i % 3000 - 1500,
    "uint16": lambda i: i % 6000,
    "int32": lambda i: 7 * i - 5000,
    "uint32": lambda i: 7 * i,
    "int64": lambda i: 11 * i - 9000,
    "uint64": lambda i: 11 * i,
    "float32": lambda i: 0.25 * i - 100.0,
    "float64": lambda i: 0.125 * i - 50.0,
}

# the tiles: origin, shape, and stride, in decimated cells
tiles = [
    # the whole raster, cell by cell
    ((0, 0), (rows, columns), (1, 1)),
    # a square piece of it
    ((3, 4), (16, 16), (1, 1)),
    # a piece taller than it is wide, whose lines need padding
    ((2, 1), (9, 5), (2, 3)),
    # and one wider than it is tall
    ((1, 2), (5, 7), (3, 2)),
]

# the intervals, which change from one tile to the next
intervals = [(-50.0, 150.0), (0.0, 1000.0), (-3000.0, 3000.0)]

# one pipeline renders every tile, so it keeps a graph per shape across cell types and intervals
pipeline = native.pipelines.Value()

# go through the cell types
for cell, value in types.items():
    # a raster of this type
    source = tile(
        cell=cell, rows=rows, columns=columns, values=(value(i) for i in range(rows * columns))
    )
    # go through the tiles
    for origin, shape, stride in tiles:
        # and the intervals
        for low, high in intervals:
            # what the iterators make of it
            expected = bytes(
                memoryview(
                    native.channels.value(
                        source=source, origin=origin, shape=shape, stride=stride, min=low, max=high
                    )
                )
            )
            # what the flow makes of it
            rendered = pipeline.render(
                source=source, origin=origin, shape=shape, stride=stride, min=low, max=high
            )
            # must be the same, byte for byte
            assert rendered == expected, (cell, origin, shape, stride, low, high)


# end of file
