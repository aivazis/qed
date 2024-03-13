# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# helpers
from .Harvester import Harvester


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

    # metamethods
    def __init__(self, channel, **kwds):
        # chain up
        super().__init__(**kwds)
        # make a harvester
        harvester = Harvester()

        # remember my configuration so we can restore it on demand
        self.viewConfiguration = harvester.harvest(component=self)
        # repeat for the visualization pipeline configuration
        self.vizConfiguration = harvester.harvest(component=channel)

        # all done
        return


# end of file
