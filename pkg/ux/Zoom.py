# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed


# the zoom control
class Zoom(qed.component, family="qed.ux.zoom.zoom", implements=qed.protocols.ux.zoom):
    """
    The state of the zoom control
    """

    # user configurable state
    horizontal = qed.properties.int()
    horizontal.default = 0
    horizontal.doc = "the horizontal zoom level"

    vertical = qed.properties.int()
    vertical.default = 0
    vertical.doc = "the vertical zoom level"

    coupled = qed.properties.bool()
    coupled.default = True
    coupled.doc = "when activated, the two levels change together"


# end of file
