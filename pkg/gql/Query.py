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


# the query
class Query(graphene.ObjectType):
    """
    The top level query
    """

    # known datasets
    readers = graphene.relay.ConnectionField(ReaderConnection)
    # server version info
    version = graphene.Field(Version, required=True)


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


    # version
    def resolve_version(root, info):
        """
        Build and return the server version
        """
        # supply the context for the {version} resolution
        return qed.meta


# end of file
