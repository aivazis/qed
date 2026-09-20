# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# my interface
from ..Node import Node

# my parts
from .Credential import Credential
from .Item import Item


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
    credentials = graphene.List(Credential)
    readers = graphene.List(graphene.String)
    items = graphene.List(Item)
    expanded = graphene.Boolean()
    pending = graphene.Boolean()
    error = graphene.String()
    hits = graphene.Int()
    dirty = graphene.Boolean()

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
    def resolve_credentials(archive, *_):
        """
        Get the archive location
        """
        # get the archive credentials
        credentials = archive.credentials()
        # go through them
        for name, value in credentials.items():
            # and convert them into credential form
            yield {"name": name, "value": value}
        # all done
        return

    @staticmethod
    def resolve_readers(archive, *_):
        """
        Get the supported readers
        """
        # extract the supported readers
        return archive.readers

    @staticmethod
    def resolve_items(archive, *_):
        """
        Get the entries of every folder of the {archive} that is on display
        """
        # the archive knows
        return archive.items()

    @staticmethod
    def resolve_expanded(archive, *_):
        """
        Check whether the root of the {archive} is on display
        """
        # the root is the archive itself
        return archive.isExpanded(uri=archive.uri)

    @staticmethod
    def resolve_pending(archive, *_):
        """
        Check whether the listing of the root of the {archive} is under way
        """
        # the root is the archive itself
        return archive.isPending(uri=archive.uri)

    @staticmethod
    def resolve_error(archive, *_):
        """
        Get the reason the listing of the root of the {archive} failed, if it did
        """
        # the root is the archive itself
        return archive.failure(uri=archive.uri)

    @staticmethod
    def resolve_dirty(archive, *_):
        """
        Check whether saving the {archive} would change what the configuration files say
        """
        # the archive keeps track
        return archive.dirty

    @staticmethod
    def resolve_hits(archive, *_):
        """
        Get the number of entries the {archive} holds in all, when it can tell
        """
        # get the listing of the root
        manifest = archive.listing(uri=archive.uri)
        # an archive that has not been listed does not know
        return None if manifest is None else manifest.hits


# end of file
