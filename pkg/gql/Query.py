# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# externals
import graphene
# support
import qed
# server version tag
from .Version import Version
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
    # known datasets
    readers = graphene.relay.ConnectionField(ReaderConnection)
    # samples
    sample = graphene.Field(Sample,
       dataset=graphene.ID(), sample=graphene.Int(), line=graphene.Int())
    # visualization pipeline
    viz = graphene.Field(VizPipeline,
       dataset=graphene.ID(), channel=graphene.String())
    # server version info
    version = graphene.Field(Version, required=True)


    # the resolvers
    # datasets
    def resolve_readers(root, info,
                        first=1, last=None, after=None, before=None,
                        **kwds):
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
        # grab the plexus
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
