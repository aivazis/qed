# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the journal
import journal

# the request payload
from .JournalChannelSetInput import JournalChannelSetInput

# the result type
from .JournalChannel import JournalChannel


# turn a journal channel on or off
class JournalChannelSet(graphene.Mutation):
    """
    Set whether a journal channel speaks

    The change applies to the server's own journal; a crew member forked afterwards inherits
    it, while one forked before keeps the state it was born with
    """

    # inputs
    class Arguments:
        # the request payload
        input = JournalChannelSetInput(required=True)

    # the result is the affected channel
    channel = graphene.Field(JournalChannel)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Set the {input.active} flag of the {input.severity} channel named {input.name}
        """
        # the channel identity
        channel = (input.severity, input.name)
        # if the severity is not one the journal knows
        if input.severity not in journal.severities:
            # complain
            raise ValueError(f"unknown journal severity '{input.severity}'")
        # open the live channel
        live = JournalChannel.live(channel=channel)
        # and set its state
        live.active = input.active
        # the device that publishes to clients keeps a census of channels; if the server has
        # one, make sure this channel is on the list from now on
        device = getattr(info.context.get("server"), "journal", None)
        # if it is there
        if device is not None:
            # add the channel
            device.channels.add(channel)
        # form the mutation resolution context
        context = {"channel": channel}
        # and resolve the mutation
        return context


# end of file
