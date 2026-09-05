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

    The change applies to the server's own journal, and the fleet passes it to every running
    crew member; a member forked afterwards inherits it
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
        # the instruction
        control = journal.control(severity=input.severity, name=input.name, active=input.active)
        # apply it here
        control.apply()
        # the server that took the request, if any
        server = info.context.get("server")
        # its fleet of crews, if it has one
        fleet = getattr(server, "fleet", None)
        # if it does
        if fleet is not None:
            # every running crew member gets the instruction too
            fleet.instruct(control=control)
        # the device that publishes to clients keeps a census of channels; if the server has
        # one, make sure this channel is on the list from now on
        device = getattr(server, "journal", None)
        # if it is there
        if device is not None:
            # add the channel
            device.channels.add(channel)
        # form the mutation resolution context
        context = {"channel": channel}
        # and resolve the mutation
        return context


# end of file
