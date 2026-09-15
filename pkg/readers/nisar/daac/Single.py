# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .SDS import SDS

# parts
from . import tokens


# the descriptor common to the single acquisition products
class Single(SDS, internal=True):
    """
    The descriptor for products formed by processing one scene
    """

    # my tokens
    level = tokens.level(default=1)
    processing = tokens.processing(allowed=("PR", "UR", "OD"))
    cycle = tokens.cycle()
    track = tokens.track()
    direction = tokens.direction()
    frame = tokens.frame()
    primaryBandwidth = tokens.bandwidth()
    secondaryBandwidth = tokens.bandwidth()
    primaryPolarization = tokens.polarization(
        allowed=("SH", "SV", "DH", "DV", "CL", "CR", "QP", "NA", "XX")
    )
    secondaryPolarization = tokens.polarization(
        allowed=("SH", "SV", "DH", "DV", "CL", "CR", "QP", "NA", "XX")
    )
    acquisition = tokens.acquisition()
    begin = tokens.ert()
    end = tokens.ert()
    fidelity = tokens.fidelity(allowed=("T", "P", "M", "N", "F", "X"))
    coverage = tokens.coverage()

    # properties
    @property
    def mark(self):
        """
        Return the timestamp that is used to place me in canonical archives
        """
        # use the start time of the acquisition
        return self.begin

    # implementation details
    @classmethod
    def sequencer(cls):
        """
        Generate the sequence of token names as they appear in valid granule ids of my type
        """
        # whatever my superclass has
        yield from super().sequencer()
        # plus all of mine
        yield from [
            # the processing type
            "processing",
            # a separator
            "separator",
            # the product type
            "product",
            # a separator
            "separator",
            # the cycle number
            "cycle",
            # a separator
            "separator",
            # the track number
            "track",
            # a separator
            "separator",
            # direction of satellite movement
            "direction",
            # a separator
            "separator",
            # frame number
            "frame",
            # a separator
            "separator",
            # primary bandwidth
            "primaryBandwidth",
            # secondary bandwidth
            "secondaryBandwidth",
            # a separator
            "separator",
            # primary polarization
            "primaryPolarization",
            # secondary polarization
            "secondaryPolarization",
            # a separator
            "separator",
            # the acquisition mode
            "acquisition",
            # a separator
            "separator",
            # the earth receive time of the beginning of the transmission
            "begin",
            # a separator
            "separator",
            # the earth receive time of the end of the transmission
            "end",
            # a separator
            "separator",
            # the CRID
            "environment",
            "phase",
            "major",
            "minor",
            "patch",
            # a separator
            "separator",
            # the product fidelity/accuracy
            "fidelity",
            # a separator
            "separator",
            # coverage
            "coverage",
            # a separator
            "separator",
            # the location of the science data system
            "sds",
            # a separator
            "separator",
            # the product counter
            "counter",
        ]
        # all done
        return


# end of file
