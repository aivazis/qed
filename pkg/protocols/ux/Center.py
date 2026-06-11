# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed


# the look-at control
class Center(qed.protocol, family="qed.ux.center"):
    """
    The source pixel that sits at the center of the viewport
    """

    # user configurable state
    row = qed.properties.float()
    row.doc = "the source row under the viewport center"

    col = qed.properties.float()
    col.doc = "the source column under the viewport center"

    # framework hooks
    @classmethod
    def pyre_default(cls, **kwds):
        """
        Pick a default implementation
        """
        # use the center base
        return qed.ux.center


# end of file
