# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# support
import qed

# my interface
from ..Node import Node

# my parts
from ..datasets.Dataset import Dataset
from .SelectorAxis import SelectorAxis


# my node type
class Reader(graphene.ObjectType):
    """
    A dataset reader
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # my fields
    id = graphene.ID()
    name = graphene.String()
    uri = graphene.String()
    api = graphene.String()
    selectors = graphene.List(SelectorAxis)
    available = graphene.List(SelectorAxis)
    datasets = graphene.List(Dataset)
    # the number of members, if this reader is a stack
    stackExtent = graphene.Int()
    # the uris of the member readers, in index order, if this reader is a stack
    members = graphene.List(graphene.String)

    # the resolvers
    @staticmethod
    def resolve_id(reader, *_):
        """
        Get the {reader} id
        """
        # splice together the {family} and {name} of the {reader}
        return f"{reader.pyre_family()}:{reader.pyre_name}"

    @staticmethod
    def resolve_name(reader, *_):
        """
        Get the {reader} name
        """
        # return the {pyre_id} of the {reader}
        return reader.pyre_name

    @staticmethod
    def resolve_uri(reader, *_):
        """
        Get the path to the file
        """
        # resolve the uri
        return str(reader.uri)

    @staticmethod
    def resolve_api(reader, *_):
        """
        Get the entry point for data requests
        """
        # requests are resolved against {data}
        return "data"

    @staticmethod
    def resolve_selectors(reader, *_):
        """
        Build a list of the selector names and their allowed values
        """
        return reader.selectors.items()

    @staticmethod
    def resolve_available(reader, *_):
        """
        Build a list of the selector names and their available values
        """
        return reader.available.items()

    @staticmethod
    def resolve_datasets(reader, *_):
        """
        Build a list of the available datasets
        """
        return reader.datasets

    @staticmethod
    def resolve_stackExtent(reader, *_):
        """
        Report the number of members if this reader is a stack, otherwise nothing
        """
        # a stack reports its member count; other readers report nothing
        return getattr(reader, "extent", None)

    @staticmethod
    def resolve_members(reader, *_):
        """
        For a stack, the uris of its member readers in index order; otherwise nothing
        """
        # get my member readers, if i am a stack
        members = getattr(reader, "readers", None)
        # a plain reader has none
        if members is None:
            # so report nothing
            return None
        # otherwise, hand off the member uris in order, so members[i] is the file at index i
        return [str(member.uri) for member in members]


# end of file
