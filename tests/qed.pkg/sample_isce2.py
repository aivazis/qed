#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the isce2 datasets sample the cells their renders visit

An unwrapped interferogram interleaves a line of amplitudes with a line of phases, and its
magnitude is the amplitude, so its sample has to see the amplitudes and nothing else, at the
stride the zoom implies; a wrapped interferogram is a raster of complex cells, whose magnitude
is their modulus. Both leave out the cells that hold no value
"""

# externals
import cmath
import math
import struct

# support
import qed

# the layout of the synthetic products
LINES, SAMPLES = 24, 32
# the amplitudes, with a hole where the product holds no value
AMPLITUDES = [
    math.nan if (line, sample) == (4, 6) else 1.0 + line * SAMPLES + sample
    for line in range(LINES)
    for sample in range(SAMPLES)
]
# the phases, far larger than any amplitude, so a sample that strayed into them would show
PHASES = [1.0e6 + line for line in range(LINES) for _ in range(SAMPLES)]
# the complex cells of the wrapped interferogram, with a hole of its own
CELLS = [
    complex(math.nan, 0) if (line, sample) == (2, 2) else cmath.rect(1.0 + line, 0.1 * sample)
    for line in range(LINES)
    for sample in range(SAMPLES)
]


def synthesize():
    """
    Write both products
    """
    # the unwrapped interferogram
    with open("sample.unw", "wb") as product:
        # goes line by line
        for line in range(LINES):
            # the span of this line
            span = slice(line * SAMPLES, (line + 1) * SAMPLES)
            # its amplitudes
            product.write(struct.pack(f"{SAMPLES}f", *AMPLITUDES[span]))
            # followed by its phases
            product.write(struct.pack(f"{SAMPLES}f", *PHASES[span]))
    # the wrapped interferogram
    with open("sample.int", "wb") as product:
        # goes cell by cell
        for cell in CELLS:
            # as a pair of floats
            product.write(struct.pack("2f", cell.real, cell.imag))
    # all done
    return


def expected(values, zoom, origin, shape):
    """
    The record the sample of the tile at {origin}+{shape} of the raster of {values} should
    produce at {zoom}, worked out the long way
    """
    # the spacing of the cells the render visits
    stride = tuple(2**level for level in zoom)
    # the magnitudes of those cells, leaving out the ones that hold no value
    magnitudes = [
        abs(values[((origin[0] + i) * stride[0]) * SAMPLES + (origin[1] + j) * stride[1]])
        for i in range(shape[0])
        for j in range(shape[1])
    ]
    # the float32 round trip of the product, so the comparison is fair
    magnitudes = [struct.unpack("f", struct.pack("f", m))[0] for m in magnitudes]
    # without the holes
    magnitudes = [m for m in magnitudes if not math.isnan(m)]
    # the count
    count = len(magnitudes)
    # the mean
    mean = sum(magnitudes) / count
    # and the second moment about it
    m2 = sum((m - mean) ** 2 for m in magnitudes)
    # assemble the record
    return float(count), min(magnitudes), mean, m2, max(magnitudes)


def close(record, reference):
    """
    Check that {record} matches {reference} to within rounding
    """
    # field by field
    return all(math.isclose(a, b, rel_tol=1e-5, abs_tol=1e-6) for a, b in zip(record, reference))


def test():
    """
    Sample both products at full resolution and zoomed out, and compare with the long way
    """
    # make the products
    synthesize()
    # the tiles to sample: a full resolution one over the hole, and a decimated one
    tiles = [((0, 0), (2, 3), (6, 8)), ((1, 1), (1, 2), (8, 8))]

    # open the unwrapped interferogram
    unw = qed.readers.isce2.unw(name="sample.unw", uri="sample.unw", shape=(LINES, SAMPLES))
    # without the statistics, which are not what is being tested
    unw.open(measure=False)
    # get its dataset
    (dataset,) = unw.datasets
    # go through the tiles
    for zoom, origin, shape in tiles:
        # sample
        record = dataset.sample(zoom=zoom, origin=origin, shape=shape)
        # the amplitudes are what it saw, holes and all
        assert close(record, expected(AMPLITUDES, zoom, origin, shape)), record

    # open the wrapped interferogram
    int_ = qed.readers.isce2.int(name="sample.int", uri="sample.int", shape=(LINES, SAMPLES))
    # without the statistics
    int_.open(measure=False)
    # get its dataset
    (dataset,) = int_.datasets
    # go through the tiles
    for zoom, origin, shape in tiles:
        # sample
        record = dataset.sample(zoom=zoom, origin=origin, shape=shape)
        # the moduli are what it saw
        assert close(record, expected(CELLS, zoom, origin, shape)), record

    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
