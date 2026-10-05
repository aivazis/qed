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
class FlowSlot(graphene.ObjectType):
    """
    A data product slot
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # metadata
    id = graphene.ID(required=True)
    # fields
    at = graphene.Field(Point, required=True)
    bound = graphene.Boolean(required=True)

    # resolvers
    @staticmethod
    def resolve_id(slot, info, **kwds):
        """
        Make an id
        """
        # splice together the {family} and {name} of the {slot}
        return slot.relay

    @staticmethod
    def resolve_at(slot, info, **kwds):
        """
        Resolve the slot position
        """
        # get the location
        x, y, z = slot.position
        # turn it into a point and return it
        return Point(x=x, y=y, z=z)


# end of file
