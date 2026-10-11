# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene
import inspect

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
from .diagram.CatalogEntry import CatalogEntry
from .diagram.CatalogGroup import CatalogGroup
from .diagram.FlowDiagram import FlowDiagram
from .diagram.PlaygroundView import PlaygroundView
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
    # the factories that can be placed on a pipeline diagram
    catalog = graphene.List(graphene.NonNull(CatalogGroup), required=True)
    # the pipeline diagram that belongs to no view
    playground = graphene.Field(FlowDiagram, required=True)
    # and how every client looks at it
    playgroundView = graphene.Field(PlaygroundView, required=True)

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

    # the playground
    @staticmethod
    def resolve_playground(store, info, **kwds):
        """
        Retrieve the pipeline diagram that belongs to no view
        """
        # the store keeps it
        return store.playground()

    @staticmethod
    def resolve_playgroundView(store, info, **kwds):
        """
        Retrieve how every client looks at the playground
        """
        # the store keeps it
        return store.playgroundView()

    @staticmethod
    def resolve_catalog(store, info, **kwds):
        """
        Describe the factories that can be placed on a pipeline diagram, grouped by the protocol
        they implement, in the order data meets them along a pipeline; each group starts with the
        protocol itself
        """
        # the groups
        groups = []
        # go through the protocols, in pipeline order
        for protocol in store.palette():
            # find the factories that implement it; some are reachable more than one way
            found = {
                implementer.pyre_family(): implementer
                for _, _, implementer in protocol.pyre_locateAllImplementers(namespace="pyre")
            }
            # describe the protocol first, followed by its implementers, sorted by family
            entries = [QED.describe(source=protocol)] + [
                QED.describe(source=found[family]) for family in sorted(found)
            ]
            # and add the group
            groups.append(
                CatalogGroup(
                    family=protocol.pyre_family(),
                    name=protocol.pyre_family().split(".")[-1],
                    entries=entries,
                )
            )
        # hand off the groups
        return groups

    @staticmethod
    def describe(source):
        """
        Describe an entry of the palette: a protocol, or a factory that implements one
        """
        # a foundry hands out the class it stands for
        factory = source() if isinstance(source, qed.foundry) else source
        # a protocol is placed unpinned; anything else is placed pinned to its class
        protocol = issubclass(factory, qed.protocol)
        # its slots are its facilities typed by a specification, in the order it declares them
        slots = [
            trait
            for trait in factory.pyre_facilities()
            if issubclass(trait.protocol, qed.flow.specification)
        ]
        # describe it
        return CatalogEntry(
            family=factory.pyre_family(),
            # a protocol is named the way the diagram names a factory pinned to nothing
            name=factory.__name__.lower() if protocol else factory.pyre_family().split(".")[-1],
            level="protocol" if protocol else "class",
            doc=inspect.cleandoc(factory.__doc__ or ""),
            inputs=[trait.name for trait in slots if trait.input],
            outputs=[trait.name for trait in slots if trait.output],
        )

    # journal channels
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
