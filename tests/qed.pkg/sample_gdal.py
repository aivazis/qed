#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a band read through GDAL samples the cells its render visits

The render reads the full resolution footprint of the tile and strides through it, so the
sample has to see exactly those cells; the band here holds unsigned cells, which the sampling
kernel reads only after widening them
"""

# externals
import math
import struct

# support
import qed

# the GDAL bindings
from osgeo import gdal

# the layout of the synthetic band
LINES, SAMPLES = 20, 28
# its values, all unsigned and spread over most of their range
VALUES = [
    (37 * line * SAMPLES + 101 * sample) % 65000
    for line in range(LINES)
    for sample in range(SAMPLES)
]


def expected(zoom, origin, shape):
    """
    The record the sample of the tile at {origin}+{shape} should produce at {zoom}, worked out
    the long way
    """
    # the spacing of the cells the render visits
    stride = tuple(2**level for level in zoom)
    # the values of those cells
    visited = [
        float(VALUES[((origin[0] + i) * stride[0]) * SAMPLES + (origin[1] + j) * stride[1]])
        for i in range(shape[0])
        for j in range(shape[1])
    ]
    # the count
    count = len(visited)
    # the mean
    mean = sum(visited) / count
    # and the second moment about it
    m2 = sum((v - mean) ** 2 for v in visited)
    # assemble the record
    return float(count), min(visited), mean, m2, max(visited)


def test():
    """
    Sample the band at full resolution and zoomed out, and compare with the long way
    """
    # let GDAL report its failures as exceptions, which is also what it will do on its own soon
    gdal.UseExceptions()
    # make a raster in memory, with one band of unsigned 16 bit cells
    raster = gdal.GetDriverByName("MEM").Create("", SAMPLES, LINES, 1, gdal.GDT_UInt16)
    # fill it
    raster.GetRasterBand(1).WriteRaster(
        0, 0, SAMPLES, LINES, struct.pack(f"{LINES * SAMPLES}H", *VALUES)
    )
    # wrap its band
    band = qed.readers.native.datasets.gdal(name="sample.gdal", rid=0, dataset=raster)
    # go through a full resolution tile and a decimated one
    for zoom, origin, shape in [((0, 0), (3, 5), (7, 9)), ((1, 1), (2, 1), (6, 8))]:
        # sample
        record = band.sample(zoom=zoom, origin=origin, shape=shape)
        # and compare
        assert all(
            math.isclose(a, b, rel_tol=1e-9) for a, b in zip(record, expected(zoom, origin, shape))
        ), record
    # the render strides the rows by the vertical scale and the columns by the horizontal one,
    # which only a zoom that differs between the axes can tell apart from the other way round
    band.measure()
    # get the channel
    channel = band.channel(name="value")
    # go through zooms that decimate one axis and not the other
    for zoom, shape in [((1, 0), (4, 8)), ((0, 1), (8, 4))]:
        # render a tile; a mix up of the axes hands the channel a tile of the wrong shape
        tile = band.render(channel=channel, zoom=zoom, origin=(0, 0), shape=shape)
        # which comes back as an encoded image with something in it
        assert len(memoryview(tile)) > 0
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
