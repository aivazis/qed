# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# externals
import graphene

# support
import qed
import journal

# my interface
from .Node import Node

# my parts
from .Archive import Archive
from .Reader import Reader


# the singleton
class QED(graphene.ObjectType):
    """
    The top level container of connected datasets and data archives
    """

    # {graphene} metadata
    class Meta:
        # register my interface
        interfaces = (Node,)

    # metadata
    id = graphene.ID(required=True)
    # my parts
    archives = graphene.List(Archive)
    readers = graphene.List(Reader)

    # resolvers
    @staticmethod
    def resolve_id(panel, info, **kwds):
        """
        Make an id
        """
        # easy enough
        return "QED"

    # data archives
    def resolve_archives(panel, info, **kwds):
        """
        Generate a sequence of known data archives
        """
        # hand off the pile of archives to the resolver
        return tuple(panel.archives.values())

    # datasets
    def resolve_readers(panel, info, **kwds):
        """
        Generate a list of all known dataset readers
        """
        # get the datasets and return them
        return tuple(panel.datasets.values())


# end of file
