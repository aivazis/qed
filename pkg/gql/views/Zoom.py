# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene

# my interface
from ..Node import Node


# my node type
class Zoom(graphene.ObjectType):
    """
    The store managed state of a dataset
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # my fields
    id = graphene.ID()
    name = graphene.ID()

    horizontal = graphene.Int()
    vertical = graphene.Int()
    coupled = graphene.Boolean()

    # resolvers
    @staticmethod
    def resolve_id(zoom, *_):
        """
        Get the {zoom} id
        """
        # splice together the {family} and {name} of the {reader}
        return f"{zoom.pyre_family()}:{zoom.pyre_name}"

    @staticmethod
    def resolve_name(zoom, *_):
        """
        Get the name of the {zoom}
        """
        # easy enough
        return zoom.pyre_name


# end of file
