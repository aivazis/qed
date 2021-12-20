# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


# externals
import graphene
# support
import qed
# server version tag
from .Version import Version
# the known datasets
from .ReaderConnection import ReaderConnection
from .Datasets import Datasets


# the query
class Query(graphene.ObjectType):
    """
    The top level query
    """

    # known datasets
    datasets = graphene.Field(Datasets, required=True)
    readers = graphene.relay.ConnectionField(ReaderConnection)
    # server version info
    version = graphene.Field(Version, required=True)


    # datasets
    def resolve_readers(root, info, **kwds):
        """
        Generate a list of all known readers
        """
        # grab the plexus
        plexus = info.context["plexus"]
        # get a list of the dataset readers and pass them on
        return list(plexus.datasets)


    def resolve_datasets(root, info, **kwds):
        """
        Generate a list of all known datasets
        """
        # this resolver must exist; its job is to build an object that gets handed to the
        # {Datasets} resolvers; here we would prep such an object using the query execution
        # context and the variable bindings in {kwds}, but for {Datasets} this is not necessary
        #
        #     root: should be {None}; this is the root
        #     info: has {.context} with whatever was built by the executioner
        #     kwds: contains the variable bindings for this resolution
        #
        return kwds


    # version
    def resolve_version(root, info):
        """
        Build and return the server version
        """
        # supply the context for the {version} resolution
        return qed.meta


# end of file
