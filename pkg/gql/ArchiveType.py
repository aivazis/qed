# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene

# my interface
from .Node import Node


# my node type
class ArchiveType(graphene.ObjectType):
    """
    A data archive type
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # my fields
    id = graphene.ID()
    name = graphene.String()
    label = graphene.String()

    # the resolvers
    @staticmethod
    def resolve_id(archive, *_):
        """
        Get the {archive} id
        """
        # use the archive {uri} to build a unique identifier
        return f"Archive:{archive.tag}"

    @staticmethod
    def resolve_name(archive, *_):
        """
        Generate the archive name
        """
        # use the component name
        return archive.tag

    @staticmethod
    def resolve_label(archive, *_):
        """
        Get the label for the archive type
        """
        # ask the archive
        return archive.label


# end of file
