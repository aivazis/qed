# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# externals
import graphene

# support
import qed
import journal

# server version tag
from .Version import Version

# the data archives
from .ArchiveConnection import ArchiveConnection

# directory contents
from .Item import Item

# the known datasets
from .ReaderConnection import ReaderConnection

# their contents
from .Sample import Sample

# and their visualization pipeline controls
from .VizPipeline import VizPipeline


# the query
class Query(graphene.ObjectType):
    """
    The top level query
    """

    # the fields
    # known data archives
    archives = graphene.relay.ConnectionField(ArchiveConnection)
    # directory contents
    contents = graphene.List(
        Item, required=True, archive=graphene.String(), path=graphene.String()
    )
    # known datasets
    readers = graphene.relay.ConnectionField(ReaderConnection)
    # samples
    sample = graphene.Field(
        Sample, dataset=graphene.ID(), sample=graphene.Int(), line=graphene.Int()
    )
    # visualization pipeline
    viz = graphene.Field(VizPipeline, dataset=graphene.ID(), channel=graphene.String())
    # server version info
    version = graphene.Field(Version, required=True)

    # the resolvers
    # data archives
    def resolve_archives(
        root, info, first=1, last=None, after=None, before=None, **kwds
    ):
        """
        Generate a sequence of known data archives
        """
        # grab the plexus
        plexus = info.context["plexus"]
        # and hand off the pile of archives to the resolver
        return plexus.archives

    # the contents of a directory
    @staticmethod
    def resolve_contents(root, info, archive, path, **kwds):
        """
        Generate a list with the contents of a directory
        """
        # this resolver must exist; its job is to build an object that gets handed to the
        # {Item} resolvers; here we prep such an object using the query execution
        # context in {info.context} and the variable bindings in {kwds}
        #
        #     root: should be {None}; this is the root
        #     info: has {.context} with whatever was built by the executioner
        #     kwds: contains the variable bindings for this query resolution
        #

        # grab the panel
        panel = info.context["panel"]
        # identify the archive
        manager = panel.archives[archive]
        # ask it for its contents
        return manager.getContents(path=qed.primitives.path(path))

    # datasets
    def resolve_readers(
        root, info, first=1, last=None, after=None, before=None, **kwds
    ):
        """
        Generate a list of all known readers
        """
        # grab the plexus
        plexus = info.context["plexus"]
        # get the datasets and return them
        return plexus.datasets

    # samples
    def resolve_sample(root, info, dataset, line, sample, **kwds):
        """
        Sample a dataset at a specified pixel
        """
        # grab the panel
        panel = info.context["panel"]
        # resolve the dataset
        dataset = panel.dataset(name=dataset)
        # assemble the sample resolution context
        context = {
            "dataset": dataset,
            "line": line,
            "sample": sample,
        }
        # and hand it to the sample resolver
        return context

    # the viz controls
    def resolve_viz(root, info, dataset, channel, **kwds):
        """
        Build a representation of the visualization controls
        """
        # grab the plexus
        panel = info.context["panel"]
        # resolve the dataset
        dataset = panel.dataset(name=dataset)
        # and the channel
        channel = dataset.channel(name=channel)
        # assemble the resolution context
        context = {
            "dataset": dataset,
            "channel": channel,
        }
        # and hand it to the resolver
        return context

    # version
    def resolve_version(root, info):
        """
        Build and return the server version
        """
        # supply the context for the {version} resolution
        return qed.meta


# end of file
