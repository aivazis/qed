# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for turning a journal channel on or off
class JournalChannelSetInput(graphene.InputObjectType):
    """
    The payload for setting whether a journal channel speaks
    """

    # the severity of the channel
    severity = graphene.String(required=True)
    # its name
    name = graphene.String(required=True)
    # whether it should speak
    active = graphene.Boolean(required=True)


# end of file
