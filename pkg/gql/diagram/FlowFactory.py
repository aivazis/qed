# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# my interface
from ..Node import Node

# field types
from .Point import Point


# the type
class FlowFactory(graphene.ObjectType):
    """
    A product factory
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # metadata
    id = graphene.ID(required=True)
    # product counts
    inputs = graphene.Int(required=True)
    outputs = graphene.Int(required=True)
    # placements
    at = graphene.Field(Point, required=True)

    # resolvers
    @staticmethod
    def resolve_id(factory, info, **kwds):
        """
        Make an id
        """
        # splice together the {family} and {name} of the {factory}
        return factory.relay

    @staticmethod
    def resolve_at(factory, info, **kwds):
        """
        Resolve the factory position
        """
        # get the location
        x, y = factory.position
        # turn it into a point and return it
        return Point(x=x, y=y)


# end of file
