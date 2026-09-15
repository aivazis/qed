# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .SDS import SDS

# parts
from . import tokens


# the RRST product descriptor
class RRST(SDS, family="qed.readers.nisar.daac.rrst"):
    """
    The RRST product descriptor
    """

    # constants
    stage = "L0A"

    # my tokens
    level = tokens.level(default=0)
    product = tokens.product(product="RRST")
    channel = tokens.channel()
    begin = tokens.ert()
    end = tokens.ert()

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
            # the product type
            "product",
            # a separator
            "separator",
            # the virtual channel identifier
            "channel",
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
    # the canonical extension for an {rrst}
    extension = ".bin"


# end of file
