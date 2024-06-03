# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed


# the flow control
class Flow(qed.protocol, family="qed.ux.flow"):
    """
    The flow layer options for a dataset
    """

    # user configurable state
    active = qed.properties.bool()
    active.doc = "indicates whether the flow layer is active"

    # framework hooks
    @classmethod
    def pyre_default(cls, **kwds):
        """
        Pick a default implementation
        """
        # use the sync base
        return qed.ux.flow


# end of file
