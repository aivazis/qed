# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene

# support
import qed
import journal

# my interface
from .Node import Node

# my parts
from .Archive import Archive
from .ArchiveType import ArchiveType
from .Reader import Reader
from . import views


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
    availableArchiveTypes = graphene.List(ArchiveType)
    views = graphene.List(views.view)
    archives = graphene.List(Archive)
    readers = graphene.List(Reader)

    # resolvers
    @staticmethod
    def resolve_id(store, info, **kwds):
        """
        Make an id
        """
        # easy enough
        return "QED"

    # available archive types
    @staticmethod
    def resolve_availableArchiveTypes(store, info, **kwds):
        """
        Retrieve the archive types for which there is runtime support
        """
        # go through the archive types for which there is runtime support
        yield from qed.archives.available()
        # all done
        return

    # views
    @staticmethod
    def resolve_views(store, info, **kwds):
        """
        Generate a sequence of the active views
        """
        # hand off the views to the resolver
        yield from (viewport.view() for viewport in store.viewports)
        # all done
        return

    # data archives
    @staticmethod
    def resolve_archives(store, info, **kwds):
        """
        Generate a sequence of known data archives
        """
        # hand off the archives to the resolver
        yield from store.archives
        # all done
        return

    # readers
    @staticmethod
    def resolve_readers(store, info, **kwds):
        """
        Generate a list of all known dataset readers
        """
        # hand off the registered readers to the resolver
        yield from store.sources
        # all done
        return


# end of file
