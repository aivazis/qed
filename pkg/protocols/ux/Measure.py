# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed


# the measure control
class Measure(qed.protocol, family="qed.ux.measure"):
    """
    The measure layer options for a dataset
    """

    # user configurable state
    active = qed.properties.bool()
    active.doc = "indicates whether the measure layer is active"

    path = qed.properties.list(schema=qed.properties.tuple(schema=qed.properties.int()))
    path.doc = "the collection of points on the pixel path"

    closed = qed.properties.bool()
    closed.doc = "indicates whether the pixel path is closed"

    selection = qed.properties.list(schema=qed.properties.int())
    selection.doc = "the indices of the selected points"

    # framework hooks
    @classmethod
    def pyre_default(cls, **kwds):
        """
        Pick a default implementation
        """
        # use the sync base
        return qed.ux.measure


# end of file
