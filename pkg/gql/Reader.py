# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


# externals
import graphene
# my interface
from .Node import Node
# my parts
from .SelectorDecl import SelectorDecl


# my node type
class Reader(graphene.ObjectType):
    """
    A dataset reader
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = Node,

    # my fields
    id = graphene.ID()
    uuid = graphene.ID()
    uri = graphene.String()
    selectors = graphene.List(SelectorDecl)


    # the resolvers
    def resolve_id(reader, *_):
        """
        Get the {reader} id
        """
        # ask relay
        return f"{reader.pyre_family()}:{reader.pyre_name}"


    def resolve_uuid(reader, *_):
        """
        Get the {reader} uuid
        """
        # ask relay
        return reader.pyre_id


    def resolve_uri(reader, *_):
        """
        Get the {uri} of the file with the datasets
        """
        # ask relay
        return reader.uri.resolve()


    def resolve_selectors(reader, *_):
        """
        Build a list of the selector names and their allowed values
        """
        return []


# end of file
