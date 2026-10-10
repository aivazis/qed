# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from ....Channel import Channel as Base


# the base of the channels of unwrapped interferograms
class Channel(Base):
    """
    The base class for the channels of isce2 unwrapped interferograms, whose datasets hold the
    amplitude and the phase as two bands of a line interleaved layout
    """

    # constants
    # the bands my recipe reads, by the name of the raster that stands for each one
    bands = {}

    # interface
    def cells(self, source) -> dict:
        """
        The bands of {source} my recipe reads, by the name of the raster that stands for each
        """
        # the plane of each band is a sub-grid that shares the mapping of the whole product
        return {name: source.data[:, band, :] for name, band in self.bands.items()}

    @staticmethod
    def layout(origin, shape, stride, band):
        """
        Lift the {origin}, {shape} and {stride} of a tile into the line interleaved layout of my
        datasets, anchored at {band}
        """
        # unpack the {tile} origin
        line, sample = origin
        # and its shape
        lines, samples = shape
        # the tile spans a single band, decimated by the stride, leaving the band axis untouched
        return (line, band, sample), (lines, 1, samples), (stride[0], 1, stride[1])


# end of file
