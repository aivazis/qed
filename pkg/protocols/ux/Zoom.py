# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed


# the zoom control
class Zoom(qed.protocol, family="qed.ux.zoom"):
    """
    The state of the zoom control
    """

    # user configurable state
    horizontal = qed.properties.float()
    horizontal.doc = "the horizontal zoom level"

    vertical = qed.properties.float()
    vertical.doc = "the vertical zoom level"

    coupled = qed.properties.bool()
    coupled.doc = "when activated, the two levels change together"

    # framework hooks
    @classmethod
    def pyre_default(cls, **kwds):
        """
        Pick a default implementation
        """
        # use the zoom base
        return qed.ux.zoom


# end of file
