# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import uuid


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

    # support
    def clone(self):
        """
        Make a copy
        """
        # make a nae
        name = str(uuid.uuid1())
        # build a new instance and return it
        return type(self)(
            name=name,
            horizontal=self.horizontal,
            vertical=self.vertical,
            coupled=self.coupled,
        )


# end of file
