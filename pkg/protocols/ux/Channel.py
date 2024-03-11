# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# my parts
from .Measure import Measure
from .Sync import Sync
from .Zoom import Zoom


# the channel ux state
class Channel(qed.protocol, family="qed.ux.channels"):
    """
    The state of a channel view
    """

    # configurable state
    measure = Measure()
    measure.doc = "the measure layer indicator"

    sync = Sync()
    sync.doc = "my sync table"

    zoom = Zoom()
    zoom.doc = "the zoom level"

    # framework hooks
    @classmethod
    def pyre_default(cls, **kwds):
        """
        Pick a default implementation
        """
        # use the sync base
        return qed.ux.channel


# end of file
