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


# the descriptor common to pair acquisition products
class Pair(SDS, internal=True):
    """
    The descriptor for products formed by processing two scenes
    """

    # my tokens, in the order they appear in the granule name
    # the product level, one unless the product says otherwise
    level = tokens.level(default=1)
    # the processing type: production, urgent response, or on demand
    processing = tokens.processing(allowed=("PR", "UR", "OD"))
    # the cycle of the reference acquisition
    referenceCycle = tokens.cycle()
    # the track within the cycle, which both acquisitions share
    track = tokens.track()
    # the direction the spacecraft was flying
    direction = tokens.direction()
    # the frame along the track
    frame = tokens.frame()
    # the cycle of the secondary acquisition
    secondaryCycle = tokens.cycle()

    # the bandwidth of the primary band
    primaryBandwidth = tokens.bandwidth()
    # and of the secondary one
    secondaryBandwidth = tokens.bandwidth()
    # the polarization
    polarization = tokens.polarization(
        allowed=("SH", "SV", "DH", "DV", "CL", "CR", "QP", "QH", "QV", "QD", "XX")
    )
    # the start of the data of the reference cycle in the file
    referenceBegin = tokens.rclk()
    # and of its end
    referenceEnd = tokens.rclk()
    # the start of the data of the secondary cycle in the file
    secondaryBegin = tokens.rclk()
    # and of its end
    secondaryEnd = tokens.rclk()
    # the accuracy and fidelity of the product
    fidelity = tokens.fidelity(allowed=("T", "P", "M", "N", "F", "X"))
    # and the coverage mode
    coverage = tokens.coverage()

    # properties
    @property
    def mark(self):
        """
        Return the timestamp that is used to place me in canonical archives
        """
        # use the start time of the reference frame
        return self.referenceBegin

    # interface
    def support(self):
        """
        My support on the timeline: the union of the intervals of the acquisitions that went into
        me, the reference one first
        """
        # the timeline
        timeline = qed.readers.nisar.timeline
        # the union of my scenes
        return qed.geometry.union(
            # the reference
            timeline.interval(begin=self.referenceBegin, end=self.referenceEnd),
            # and the secondary
            timeline.interval(begin=self.secondaryBegin, end=self.secondaryEnd),
        )

    def lies(self, places):
        """
        Check whether i lie on one of the {places}, a set of (track, direction, frame) triples,
        with the direction spelled as its initial
        """
        # by my track, direction and frame, which both my scenes share
        return (self.track, self.direction, self.frame) in places

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
            # the start of the data of the reference cycle in the file
            "referenceBegin",
            # a separator
            "separator",
            # the end of the data of the reference cycle in the file
            "referenceEnd",
            # a separator
            "separator",
            # the start of the data of the secondary cycle in the file
            "secondaryBegin",
            # a separator
            "separator",
            # the end of the data of the secondary cycle in the file
            "secondaryEnd",
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
