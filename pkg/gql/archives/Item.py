# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# my interface
from ..Node import Node


# my node type
class Item(graphene.ObjectType):
    """
    An entry of a data archive: a folder or a file, along with the folder that holds it and,
    for folders, where its own listing stands
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # my fields
    id = graphene.ID()
    name = graphene.String()
    uri = graphene.String()
    isFolder = graphene.Boolean()
    parent = graphene.String()
    expanded = graphene.Boolean()
    pending = graphene.Boolean()
    error = graphene.String()

    # the resolvers
    @staticmethod
    def resolve_id(item: dict, *_):
        """
        Get the {item} id
        """
        # use the {uri} to build a unique identifier
        return f"Item:{item['uri']}"

    @staticmethod
    def resolve_name(item: dict, *_):
        """
        Get the {item} name
        """
        # easy enough
        return item["name"]

    @staticmethod
    def resolve_uri(item: dict, *_):
        """
        Get the {item} uri
        """
        # easy enough
        return item["uri"]

    @staticmethod
    def resolve_isFolder(item: dict, *_):
        """
        Separate files from folders
        """
        # easy enough
        return item["isFolder"]

    @staticmethod
    def resolve_parent(item: dict, *_):
        """
        Get the uri of the folder that holds the {item}
        """
        # easy enough
        return item["parent"]

    @staticmethod
    def resolve_expanded(item: dict, *_):
        """
        Check whether the {item} is a folder on display
        """
        # easy enough
        return item["expanded"]

    @staticmethod
    def resolve_pending(item: dict, *_):
        """
        Check whether the listing of the {item} is under way
        """
        # easy enough
        return item["pending"]

    @staticmethod
    def resolve_error(item: dict, *_):
        """
        Get the reason the listing of the {item} failed, if it did
        """
        # easy enough
        return item["error"]


# end of file
