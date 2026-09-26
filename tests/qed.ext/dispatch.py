#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise the dispatch of a buffer to the kernel for its cell type

The struct module spells some integers more than one way: an eight byte signed integer is 'l'
on most hosts when numpy exports it, and 'q' when it is a long long, and the same goes for
the unsigned ones. Both spellings, every width of signed and unsigned integer, and both
precisions of floating point and complex cells have to reach their kernels, and a cell type no
kernel holds has to be refused by name
"""

# externals
import numpy

# support
import qed

# the kernels
native = qed.libqed.native

# every cell type the native kernels hold, as numpy spells them, including both spellings of
# the eight byte integers
types = [
    numpy.int8,
    numpy.int16,
    numpy.int32,
    numpy.int64,
    numpy.longlong,
    numpy.uint8,
    numpy.uint16,
    numpy.uint32,
    numpy.uint64,
    numpy.ulonglong,
    numpy.float32,
    numpy.float64,
]

# go through them
for cell in types:
    # a 4x4 ramp of this type
    ramp = numpy.arange(16).astype(cell).reshape(4, 4)
    # sample every other cell in each direction: the values 0, 2, 8, 10
    record = native.sample(source=ramp, origin=(0, 0), shape=(2, 2), stride=(2, 2))
    # four samples, from 0 to 10, with mean 5 and second moment 68
    assert record == (4.0, 0.0, 5.0, 68.0, 10.0), (cell, memoryview(ramp).format, record)

# the complex cells, of both precisions
for cell in (numpy.complex64, numpy.complex128):
    # a tile with magnitudes 5, 0, 0, 10
    z = numpy.array([[3 + 4j, 0], [0, 6 + 8j]], dtype=cell)
    # is sampled by magnitude
    count, low, mean, m2, high = native.sample(source=z, origin=(0, 0), shape=(2, 2), stride=(1, 1))
    # four samples spanning 0 to 10, with mean 15/4 and the matching second moment
    assert (count, low, high) == (4.0, 0.0, 10.0) and abs(mean - 3.75) < 1e-6
    assert abs(m2 - 68.75) < 1e-6

# the real valued channels render every integer width, signed and unsigned
for cell in (numpy.int8, numpy.uint8, numpy.uint16, numpy.uint32, numpy.uint64, numpy.int64):
    # a 4x4 ramp of this type
    ramp = numpy.arange(16).astype(cell).reshape(4, 4)
    # through both of them
    for channel in (native.channels.value, native.channels.abs):
        # render a 2x2 tile
        tile = channel(source=ramp, origin=(0, 0), shape=(2, 2), stride=(2, 2), min=0, max=15)
        # which comes back as an encoded image with something in it
        assert len(memoryview(tile)) > 0, (cell, channel)

# a cell type no kernel holds
flags = numpy.zeros((4, 4), dtype=numpy.bool_)
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
