# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed


# the channel ux state
class Channel(qed.component, family="qed.ux.channels.channel"):
    """
    The state of a channel view
    """

    # configurable state
    measure = qed.protocols.ux.measure()
    measure.doc = "the measure layer indicator"

    sync = qed.protocols.ux.sync()
    sync.doc = "my sync table"

    zoom = qed.protocols.ux.zoom()
    zoom.doc = "the zoom level"


# end of file
