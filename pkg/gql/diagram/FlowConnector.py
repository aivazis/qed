# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene

# my interface
from ..Node import Node

# field types
from .Point import Point


# the type
class FlowConnector(graphene.ObjectType):
    """
    A connector
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # metadata
    id = graphene.ID(required=True)
    # fields
    input = graphene.Boolean(required=True)
    slot = graphene.Field(Point, required=True)
    factory = graphene.Field(Point, required=True)

    # resolvers
    @staticmethod
    def resolve_id(connector, info, **kwds):
        """
        Make an id
        """
        # splice together the {family} and {name} of the {connector}
        return connector.relay

    @staticmethod
    def resolve_input(connector, info, **kwds):
        """
        Resolve the connector type
        """
        # easy enough
        return connector.typename() == "Input"

    @staticmethod
    def resolve_factory(connector, info, **kwds):
        """
        Resolve the connector factory position
        """
        # get the location
        x, y = connector.factory.position
        # turn it into a point and return it
        return Point(x=x, y=y)

    @staticmethod
    def resolve_slot(connector, info, **kwds):
        """
        Resolve the connector slot position
        """
        # get the location
        x, y = connector.slot.position
        # turn it into a point and return it
        return Point(x=x, y=y)


# end of file
