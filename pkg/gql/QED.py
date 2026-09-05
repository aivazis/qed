# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# support
import qed
import journal

# my interface
from .Node import Node

# my parts
from .archives.Archive import Archive
from .archives.ArchiveType import ArchiveType
from .readers.Reader import Reader
from .journal.JournalChannel import JournalChannel
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
    journal = graphene.List(JournalChannel)

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

    # journal channels
    @staticmethod
    def resolve_journal(store, info, **kwds):
        """
        Generate the journal channels the server knows about, as (severity, name) pairs

        The live channel index is not enumerable, so the list is the union of the channels the
        application placed under user control and the channels that have spoken since the
        server started, which the device that publishes to clients keeps a census of
        """
        # the pile
        channels = set()
        # the application, if the request came through a server
        server = info.context.get("server")
        # the device that publishes to clients, if the server installed one
        device = getattr(server, "journal", None)
        # if it is there
        if device is not None:
            # its census
            channels |= device.channels
        # the application
        plexus = info.context.get("plexus")
        # if it is there
        if plexus is not None:
            # the channels it declared
            channels |= {(severity, name) for severity, name in plexus.pyre_journalChannels()}
        # hand them over, in a stable order
        yield from sorted(channels)
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
