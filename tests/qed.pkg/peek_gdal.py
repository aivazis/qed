#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that peeking into a band of real cells read through GDAL reports the channels the band
has, rather than every channel its cell type lists in its summary

A band read through GDAL renders only through the channels that can draw a GDAL tile, so the
summary of a real cell names a channel, {abs}, that the band never builds
"""

# externals
import struct

# support
import qed

# the GDAL bindings
from osgeo import gdal

# the layout of the synthetic band
LINES, SAMPLES = 6, 8


def test():
    """
    Peek into a band of real cells, and ask for its summary
    """
    # let GDAL report its failures as exceptions, which is also what it will do on its own soon
    gdal.UseExceptions()
    # make a raster in memory, with one band of real cells
    raster = gdal.GetDriverByName("MEM").Create("", SAMPLES, LINES, 1, gdal.GDT_Float32)
    # fill it with values that identify their cell
    raster.GetRasterBand(1).WriteRaster(
        0, 0, SAMPLES, LINES, struct.pack(f"{LINES * SAMPLES}f", *range(LINES * SAMPLES))
    )
    # wrap its band
    band = qed.readers.native.datasets.gdal(name="peek.gdal", rid=0, dataset=raster)
    # the summary of its cell type names a channel the band does not have
    assert "abs" in band.cell.summary
    assert "abs" not in band.channels

    # peek at a cell, collecting the representations each channel produces
    reps = {name: list(rep) for name, rep in band.peek(pixel=(3, 5))}
    # the cursor is reported
    assert "cursor" in reps
    # and so is the value, read from the right cell
    assert "value" in reps
    assert float(reps["value"][0][0]) == 3 * SAMPLES + 5
    # but nothing about the channel the band does not have
    assert "abs" not in reps

    # the summary holds only the channels the band has
    names = [channel.tag for channel in band.summary()]
    # which is just the value
    assert names == ["value"], names

    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
