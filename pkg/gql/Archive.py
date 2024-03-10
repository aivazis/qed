# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene

# my interface
from .Node import Node


# my node type
class Archive(graphene.ObjectType):
    """
    A data archive
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # my fields
    id = graphene.ID()
    name = graphene.String()
    uri = graphene.String()
    readers = graphene.List(graphene.String)

    # the resolvers
    @staticmethod
    def resolve_id(archive, *_):
        """
        Get the {archive} id
        """
        # use the archive {uri} to build a unique identifier
        return f"Archive:{archive.uri}"

    @staticmethod
    def resolve_name(archive, *_):
        """
        Generate the archive name
        """
        # use the component name
        return archive.pyre_name

    @staticmethod
    def resolve_uri(archive, *_):
        """
        Get the archive location
        """
        # convert the archive URI into a string
        return f"{archive.uri}"

    @staticmethod
    def resolve_readers(archive, *_):
        """
        Get the supported readers
        """
        # extract the supported readers
        return archive.readers


# end of file
