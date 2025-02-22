# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene

# my interface
from .Node import Node

# my fields
from .Controller import Controller


# my node type
class Channel(graphene.ObjectType):
    """
    A dataset channel
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # my fields
    id = graphene.ID()
    name = graphene.ID()
    tag = graphene.String()
    controllers = graphene.List(Controller)

    # resolvers
    @staticmethod
    def resolve_id(channel, *_):
        """
        Get the {channel} id
        """
        # splice together the {family} and {name} of the {channel}
        return f"{channel.pyre_family()}:{channel.pyre_name}"

    @staticmethod
    def resolve_name(channel, *_):
        """
        Get the name of the channel
        """
        # easy enough
        return channel.pyre_name

    @staticmethod
    def resolve_controllers(channel, *_):
        """
        Get the channel controllers
        """
        # go  through the controllers
        for controller, trait in channel.controllers():
            # pack into a resolution context
            context = {
                "controller": controller,
                "trait": trait,
            }
            # and resolve it
            yield context
        # all done
        return


# end of file
