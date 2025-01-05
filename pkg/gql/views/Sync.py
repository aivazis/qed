# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene

# my interface
from ..Node import Node

# my parts
from ..Pixel import Pixel


# my node type
class Sync(graphene.ObjectType):
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

    dirty = graphene.Boolean()
    channel = graphene.Boolean()
    zoom = graphene.Boolean()
    scroll = graphene.Boolean()
    path = graphene.Boolean()
    offsets = graphene.Field(Pixel)

    # resolvers
    @staticmethod
    def resolve_id(sync, *_):
        """
        Get the {sync} id
        """
        # splice together the {family} and {name} of the {reader}
        return f"{sync.pyre_family()}:{sync.pyre_name}"

    @staticmethod
    def resolve_name(sync, *_):
        """
        Get the name of the {sync}
        """
        # easy enough
        return sync.pyre_name


# end of file
