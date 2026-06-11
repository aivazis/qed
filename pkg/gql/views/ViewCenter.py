# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# my interface
from ..Node import Node


# my node type
class ViewCenter(graphene.ObjectType):
    """
    A view's look-at center
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # my fields
    id = graphene.ID()
    name = graphene.String()

    dirty = graphene.Boolean()
    row = graphene.Float()
    col = graphene.Float()

    # resolvers
    @staticmethod
    def resolve_id(center, *_):
        """
        Get the {center} id
        """
        # splice together the {family} and {name} of the {center}
        return f"{center.pyre_family()}:{center.pyre_name}"

    @staticmethod
    def resolve_name(center, *_):
        """
        Get the name of the {center}
        """
        # easy enough
        return center.pyre_name


# end of file
