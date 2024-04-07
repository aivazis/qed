# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# helpers
from .Harvester import Harvester


# the channel ux state
class Channel(
    qed.component, family="qed.ux.channels.channel", implements=qed.protocols.ux.channel
):
    """
    The state of a channel view
    """

    # metamethods
    def __init__(self, channel, **kwds):
        # chain up
        super().__init__(**kwds)
        # remember the visualization pipeline configuration so we can restore it on demand
        self.configuration = self.harvester.harvest(component=channel)
        # all done
        return

    # singleton
    # the state harvester
    harvester = Harvester()


# end of file
