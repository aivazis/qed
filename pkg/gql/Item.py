# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# externals
import graphene

# my interface
from .Node import Node


# my node type
class Item(graphene.ObjectType):
    """
    A repository item
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # my fields
    id = graphene.ID()
    name = graphene.ID()
    uri = graphene.String()
    isFolder = graphene.Boolean()

    # the resolvers
    @staticmethod
    def resolve_id(item: tuple, *_):
        """
        Get the {item} id
        """
        # unpack
        fs, name, node = item
        # use the {uri} to build a unique identifier
        return f"Item:{node.uri}"

    @staticmethod
    def resolve_name(item: tuple, *_):
        """
        Get the {item} name
        """
        # unpack
        fs, name, node = item
        # use the {uri} to build a unique identifier
        return name

    @staticmethod
    def resolve_uri(item: tuple, *_):
        """
        Get the {item} name
        """
        # unpack
        fs, name, node = item
        # use the {uri} to build a unique identifier
        return node.uri

    @staticmethod
    def resolve_isFolder(item: tuple, *_):
        """
        Get the {item} name
        """
        # unpack
        fs, name, node = item
        # use the {uri} to build a unique identifier
        return node.isFolder


# end of file
