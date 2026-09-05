# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the journal
import journal

# my interface
from ..Node import Node


# a journal channel and its state
class JournalChannel(graphene.ObjectType):
    """
    A journal channel the server knows about, and whether it speaks

    The channel is identified by its severity and name; the state is read from the live
    journal every time, so the answer is always current
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # my fields
    id = graphene.ID(required=True)
    severity = graphene.String(required=True)
    name = graphene.String(required=True)
    active = graphene.Boolean(required=True)
    fatal = graphene.Boolean(required=True)

    # resolvers; the source is a (severity, name) pair
    @staticmethod
    def resolve_id(channel, info, **kwds):
        """
        Make an id out of the channel identity
        """
        # unpack
        severity, name = channel
        # and join
        return f"{severity}:{name}"

    @staticmethod
    def resolve_severity(channel, info, **kwds):
        """
        The severity of the channel
        """
        # easy enough
        return channel[0]

    @staticmethod
    def resolve_name(channel, info, **kwds):
        """
        The name of the channel
        """
        # easy enough
        return channel[1]

    @staticmethod
    def resolve_active(channel, info, **kwds):
        """
        Whether the channel speaks
        """
        # ask the live channel
        return JournalChannel.live(channel=channel).active

    @staticmethod
    def resolve_fatal(channel, info, **kwds):
        """
        Whether the channel aborts after speaking
        """
        # ask the live channel
        return JournalChannel.live(channel=channel).fatal

    # implementation details
    @staticmethod
    def live(channel):
        """
        Open the journal channel that {channel} identifies
        """
        # unpack
        severity, name = channel
        # find the factory
        factory = journal.severities[severity]
        # and open the channel; the state is shared by everybody with this name
        return factory(name)


# end of file
