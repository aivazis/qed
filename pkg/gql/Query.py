# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene
# support
import qed
# server version tag
from .Version import Version
# the known datasets
from .ReaderConnection import ReaderConnection
# and their contents
from .Sample import Sample


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
    def resolve_sample(root, info,
                       dataset, line, sample,
                       **kwds):
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
        # just fake it, for now
        return context


    # version
    def resolve_version(root, info):
        """
        Build and return the server version
        """
        # supply the context for the {version} resolution
        return qed.meta


# end of file
