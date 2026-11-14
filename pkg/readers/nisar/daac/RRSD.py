# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .SDS import SDS

# parts
from . import tokens


# the RRSD product descriptor
class RRSD(SDS, family="qed.readers.nisar.daac.rrsd"):
    """
    The RRSD product descriptor
    """

    # constants
    stage = "L0B"

    # my tokens, in the order they appear in the granule name
    # the product level, zero for these
    level = tokens.level(default=0)
    # the product type
    product = tokens.product(product="RRSD")
    # the processing type: production or urgent response
    processing = tokens.processing(allowed=("PR", "UR"))
    # the cycle of the acquisition
    cycle = tokens.cycle()
    # its track within the cycle
    track = tokens.track()
    # the direction the spacecraft was flying
    direction = tokens.direction()
    # the radar configuration mode
    rcid = tokens.rcid()
    # the radar processing mode
    radarProcessing = tokens.radarProcessing()
    # the time of the first rangeline in the file
    begin = tokens.rangeline()
    # and of the last
    end = tokens.rangeline()
    # and the accuracy and fidelity of the product
    fidelity = tokens.fidelity(allowed=("T", "P", "M", "N", "F", "X"))

    # properties
    @property
    def mark(self):
        """
        Return the timestamp that is used to place me in canonical archives
        """
        # use the start time of the acquisition
        return self.begin

    # interface
    def support(self):
        """
        My support on the timeline: the interval of the acquisition in me
        """
        # from the start of my data to its end
        return qed.readers.nisar.timeline.interval(begin=self.begin, end=self.end)

    def lies(self, places):
        """
        Check whether i lie on one of the {places}, a set of (track, direction, frame) triples,
        with the direction spelled as its initial; my data are not cut into frames, so any frame
        of my track and direction will do
        """
        # by my track and direction
        return any(
            (track, direction) == (self.track, self.direction) for track, direction, _ in places
        )

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
            # the radar configuration mode
            "rcid",
            # the radar processing mode
            "radarProcessing",
            # a separator
            "separator",
            # the radar time of the start of the data
            "begin",
            # a separator
            "separator",
            # the radar time of the end of the data
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
            # the product fidelity/accuracy
            "fidelity",
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
