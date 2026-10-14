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
from .FlowProduct import FlowProduct
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
    # how far down its product is pinned: "protocol", "class", or "instance", which is also the
    # level of a trait's own slot on an instance that holds a product; none otherwise
    level = graphene.String()
    # whether an instance is behind the slot, and it holds nothing
    empty = graphene.Boolean(required=True)
    # whether the product it holds is stale; none when it holds no product
    stale = graphene.Boolean()
    # what it holds, as the inspector shows it
    product = graphene.Field(FlowProduct, required=True)

    # resolvers
    @staticmethod
    def resolve_id(slot, info, **kwds):
        """
        Make an id
        """
        # splice together the {family} and {name} of the {slot}
        return slot.relay

    @staticmethod
    def resolve_level(slot, info, **kwds):
        """
        Get how far down what the slot holds is pinned
        """
        # the slot knows
        return slot.level()

    @staticmethod
    def resolve_empty(slot, info, **kwds):
        """
        Decide whether there is an instance behind the slot that holds nothing in it
        """
        # the way the inspector does
        return FlowProduct.resolve_empty(slot, info, **kwds)

    @staticmethod
    def resolve_stale(slot, info, **kwds):
        """
        Decide whether the product the slot holds is stale, if it holds one
        """
        # the way the inspector does
        return FlowProduct.resolve_stale(slot, info, **kwds)

    @staticmethod
    def resolve_product(slot, info, **kwds):
        """
        Describe what the slot holds
        """
        # the slot itself has everything the description needs
        return slot

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
