# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed


# the sync control
class Sync(qed.protocol, family="qed.ux.sync"):
    """
    The sync options for a dataset
    """

    # user configurable state
    channel = qed.properties.bool()
    channel.doc = "the channel sync flag"

    zoom = qed.properties.bool()
    zoom.doc = "the zoom sync flag"

    scroll = qed.properties.bool()
    scroll.doc = "the scroll sync flag"

    path = qed.properties.bool()
    path.doc = "the path sync flag"

    offsets = qed.properties.tuple(schema=qed.properties.int())
    offsets.doc = (
        "relative offset to apply to this viewport when synchronized scrolling"
    )

    # framework hooks
    @classmethod
    def pyre_default(cls, **kwds):
        """
        Pick a default implementation
        """
        # use the sync base
        return qed.ux.sync


# end of file
