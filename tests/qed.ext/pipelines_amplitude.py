#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Render tiles of the amplitude of a complex raster through the flow pipeline and through the
iterators, and check that the two encode the same bytes: for both complex cell types, for tiles
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


# the value of a cell: magnitudes that sweep a few decades, at phases that wander around the
# circle, so the magnitude depends on both parts
def value(i):
    """
    The value of cell {i}
    """
    # the parts
    return complex(0.37 * (i % 97) - 11.0, 0.21 * (i % 89) - 7.5)


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

# the intervals of magnitudes, which change from one tile to the next
intervals = [(0.0, 20.0), (1.0, 5.0), (0.5, 40.0)]

# go through the complex cell types
for cell in ("complex64", "complex128"):
    # one pipeline renders every tile, so it keeps a graph per shape across intervals
    pipeline = getattr(native.pipelines, cell).Amplitude()
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
                    native.channels.amplitude(
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

# a pipeline refuses a raster of the other complex type
try:
    # by its dispatcher
    native.pipelines.complex64.Amplitude().render(
        source=tile(cell="complex128", rows=2, columns=2, values=[1j] * 4),
        origin=(0, 0),
        shape=(2, 2),
        stride=(1, 1),
        min=0.0,
        max=1.0,
    )
# with a complaint
except ValueError:
    # as it should
    pass
# and nothing else is acceptable
else:
    # so a quiet acceptance is a failure
    raise AssertionError("a complex128 raster was accepted by a complex64 pipeline")


# end of file
