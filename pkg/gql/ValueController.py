# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene
# my interface
from .Node import Node


# a controller that captures a single value
class ValueController(graphene.ObjectType):
    """
    A controller that captures a single value
    """


    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = Node,

    # my fields
    id = graphene.ID()
    uuid = graphene.ID()
    # payload
    slot = graphene.String()
    min = graphene.Float()
    max = graphene.Float()
    value = graphene.Float()


    # the resolvers
    def resolve_id(channel, *_):
        """
        Get the {channel} id
        """
        # splice together the {family} and {name} of the {channel}
        return f"{channel.pyre_family()}:{channel.pyre_name}"


    def resolve_uuid(channel, *_):
        """
        Get the {channel} uuid
        """
        # return the {pyre_id} of the {channel}
        return channel.pyre_id


# end of file
