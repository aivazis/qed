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


# the descriptor common to the single acquisition products
class Single(SDS, internal=True):
    """
    The descriptor for products formed by processing one scene
    """

    # my tokens, in the order they appear in the granule name
    # the product level, one unless the product says otherwise
    level = tokens.level(default=1)
    # the processing type: production, urgent response, or on demand
    processing = tokens.processing(allowed=("PR", "UR", "OD"))
    # the cycle of the acquisition
    cycle = tokens.cycle()
    # its track within the cycle
    track = tokens.track()
    # the direction the spacecraft was flying
    direction = tokens.direction()
    # the frame along the track
    frame = tokens.frame()
    # the bandwidth of the primary band
    primaryBandwidth = tokens.bandwidth()
    # and of the secondary one
    secondaryBandwidth = tokens.bandwidth()
    # the polarization of the primary band, among the codes of sections 3.7 and 3.8 of the naming
    # conventions, since the archives hold single products in the quasi polarizations of 3.8
    primaryPolarization = tokens.polarization(
        allowed=("SH", "SV", "DH", "DV", "CL", "CR", "QP", "QH", "QV", "QD", "NA", "XX")
    )
    # and of the secondary one
    secondaryPolarization = tokens.polarization(
        allowed=("SH", "SV", "DH", "DV", "CL", "CR", "QP", "QH", "QV", "QD", "NA", "XX")
    )
    # the acquisition mode
    acquisition = tokens.acquisition()
    # the radar time of the start of the data processed as zero doppler
    begin = tokens.zeroDoppler()
    # and of its end
    end = tokens.zeroDoppler()
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
        # use the start time of the acquisition
        return self.begin

    # interface
    def support(self):
        """
        My support on the timeline: the interval of the acquisition that went into me
        """
        # from the start of my scene to its end
        return qed.readers.nisar.timeline.interval(begin=self.begin, end=self.end)

    def lies(self, places):
        """
        Check whether i lie on one of the {places}, a set of (track, direction, frame) triples,
        with the direction spelled as its initial
        """
        # by my track, direction and frame
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
            # the radar time of the start of the data, processed to zero Doppler
            "begin",
            # a separator
            "separator",
            # the radar time of the end of the data, processed to zero Doppler
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
