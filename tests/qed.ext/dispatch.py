#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise the dispatch of a buffer to the kernel for its cell type

The struct module spells some integers more than one way: an eight byte signed integer is 'l'
on most hosts and 'q' when it is a long long, and the same goes for the unsigned ones. Both
spellings, every width of signed and unsigned integer, and both precisions of floating point
and complex cells have to reach their kernels, and a cell type no kernel holds has to be
refused by name
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


def spelled(g, code):
    """
    View the cells of the rank 2 grid {g} under the struct {code}, another spelling of their type
    """
    # recast the bytes of the grid under the other spelling
    return memoryview(g).cast("B").cast(code, g.shape)


# the kernels
native = qed.libqed.native

# every cell type the native kernels hold, as pyre names them
cells = [
    "int8",
    "int16",
    "int32",
    "int64",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "float32",
    "float64",
]
# a 4x4 ramp of each
ramps = [(cell, tile(cell=cell, rows=4, columns=4, values=range(16))) for cell in cells]
# pyre spells its eight byte integers 'q' and 'Q'; add the ramps that spell them 'l' and 'L'
ramps += [
    (code, spelled(g=tile(cell=cell, rows=4, columns=4, values=range(16)), code=code))
    for cell, code in (("int64", "l"), ("uint64", "L"))
]

# go through them
for cell, ramp in ramps:
    # sample every other cell in each direction: the values 0, 2, 8, 10
    record = native.sample(source=ramp, origin=(0, 0), shape=(2, 2), stride=(2, 2))
    # four samples, from 0 to 10, with mean 5 and second moment 68
    assert record == (4.0, 0.0, 5.0, 68.0, 10.0), (cell, memoryview(ramp).format, record)

# the complex cells, of both precisions
for cell in ("complex64", "complex128"):
    # a tile with magnitudes 5, 0, 0, 10
    z = tile(cell=cell, rows=2, columns=2, values=[3 + 4j, 0, 0, 6 + 8j])
    # is sampled by magnitude
    count, low, mean, m2, high = native.sample(source=z, origin=(0, 0), shape=(2, 2), stride=(1, 1))
    # four samples spanning 0 to 10, with mean 15/4 and the matching second moment
    assert (count, low, high) == (4.0, 0.0, 10.0) and abs(mean - 3.75) < 1e-6
    assert abs(m2 - 68.75) < 1e-6

# the real valued channels render every integer width, signed and unsigned
for cell in ("int8", "uint8", "uint16", "uint32", "uint64", "int64"):
    # a 4x4 ramp of this type
    ramp = tile(cell=cell, rows=4, columns=4, values=range(16))
    # through both of them
    for channel in (native.channels.value, native.channels.abs):
        # render a 2x2 tile
        image = channel(source=ramp, origin=(0, 0), shape=(2, 2), stride=(2, 2), min=0, max=15)
        # which comes back as an encoded image with something in it
        assert len(memoryview(image)) > 0, (cell, channel)

# a cell type no kernel holds
flags = memoryview(bytes(16)).cast("?", (4, 4))
# is refused
try:
    # by the dispatcher
    native.sample(source=flags, origin=(0, 0), shape=(2, 2), stride=(1, 1))
# with a complaint that names the cell type
except ValueError as error:
    # which is how the caller learns what went wrong
    assert "unsupported grid cell type" in str(error)
# and nothing else is acceptable
else:
    # so a quiet acceptance is a failure
    raise AssertionError("a boolean buffer was accepted")


# end of file
