# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .SDS import SDS

# parts
from . import tokens


# the descriptor common to pair acquisition products
class Pair(SDS, internal=True):
    """
    The descriptor for products formed by processing two scenes
    """

    # my tokens
    level = tokens.level(default=1)
    processing = tokens.processing(allowed=("PR", "UR", "OD"))
    referenceCycle = tokens.cycle()
    track = tokens.track()
    direction = tokens.direction()
    frame = tokens.frame()
    secondaryCycle = tokens.cycle()

    primaryBandwidth = tokens.bandwidth()
    secondaryBandwidth = tokens.bandwidth()
    polarization = tokens.polarization(
        allowed=("SH", "SV", "DH", "DV", "CL", "CR", "QP", "QH", "QV", "QD", "XX")
    )
    referenceBegin = tokens.ert()
    referenceEnd = tokens.ert()
    secondaryBegin = tokens.ert()
    secondaryEnd = tokens.ert()
    fidelity = tokens.fidelity(allowed=("T", "P", "M", "N", "F", "X"))
    coverage = tokens.coverage()

    # properties
    @property
    def mark(self):
        """
        Return the timestamp that is used to place me in canonical archives
        """
        # use the start time of the reference frame
        return self.referenceBegin

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
            # the reference cycle number
            "referenceCycle",
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
            # the secondary cycle number
            "secondaryCycle",
            # a separator
            "separator",
            # primary bandwidth
            "primaryBandwidth",
            # secondary bandwidth
            "secondaryBandwidth",
            # a separator
            "separator",
            # polarization
            "polarization",
            # a separator
            "separator",
            # the earth receive time of the beginning of the transmission
            "referenceBegin",
            # a separator
            "separator",
            # the earth receive time of the end of the transmission
            "referenceEnd",
            # a separator
            "separator",
            # the earth receive time of the beginning of the transmission
            "secondaryBegin",
            # a separator
            "separator",
            # the earth receive time of the end of the transmission
            "secondaryEnd",
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
