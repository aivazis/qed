# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .SDS import SDS

# parts
from . import tokens


# the descriptor
class HST_DRT(SDS, family="qed.readers.nisar.daac.hst_drt"):
    """
    The HST_DRT descriptor
    """

    # constants
    stage = "L0B"

    # my tokens, in the order they appear in the granule name
    # the product level, zero for these
    level = tokens.level(default=0)
    # the product type
    product = tokens.product(product="HST_DRT")
    # the processing type: production or urgent response
    processing = tokens.processing(allowed=("PR", "UR"))
    # the cycle of the acquisition
    cycle = tokens.cycle()
    # its track within the cycle
    track = tokens.track()
    # the direction the spacecraft was flying
    direction = tokens.direction()
    # the radar start time of the data in the file, from the pre-take
    begin = tokens.datatake()
    # and its end time, from the post-take
    end = tokens.datatake()

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
            # the radar start time of the data in the file, from the pre-take
            "begin",
            # a separator
            "separator",
            # the radar end time of the data in the file, from the post-take
            "end",
            # a separator
            "separator",
            # the CRID
            "environment",
            "major",
            "minor",
            "patch",
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

    # constants
    # the canonical extension for an {hst_drt}
    extension = ".bin"


# end of file
