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

# the connectors, whose labels follow their slots
from ...ux.diagram.Connector import Connector


# the type
class FlowLabel(graphene.ObjectType):
    """
    A label
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # metadata
    id = graphene.ID(required=True)
    # fields
    at = graphene.Field(Point, required=True)
    value = graphene.List(graphene.String, required=True)
    category = graphene.String(required=True)
    # the id of the node it follows when that node is dragged
    owner = graphene.ID()

    # resolvers
    @staticmethod
    def resolve_id(label, info, **kwds):
        """
        Make an id
        """
        # splice together the {family} and {name} of the {label}
        return label.relay

    @staticmethod
    def resolve_value(label, info, **kwds):
        """
        Get the label text
        """
        # easy enough
        return label.text

    @staticmethod
    def resolve_owner(label, info, **kwds):
        """
        Get the id of the node the label follows
        """
        # the entity the label belongs to
        owner = label.owner
        # the label of a connector sits next to its slot, so it follows the slot
        if isinstance(owner, Connector):
            # whichever one that is now
            owner = owner.slot
        # hand off its id, if there is one
        return None if owner is None else owner.relay

    @staticmethod
    def resolve_at(label, info, **kwds):
        """
        Resolve the label position
        """
        # get the location
        x, y, z = label.position
        # turn it into a point and return it
        return Point(x=x, y=y, z=z)


# end of file
