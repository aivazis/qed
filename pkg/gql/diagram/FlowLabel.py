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
    def resolve_at(label, info, **kwds):
        """
        Resolve the label position
        """
        # get the location
        x, y = label.position
        # turn it into a point and return it
        return Point(x=x, y=y)


# end of file
