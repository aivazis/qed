# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# my parts
from .Build import Build


# the server
class Server(graphene.ObjectType):
    """
    What the server is doing, one subsystem at a time
    """

    # the preparation of every dataset a client has asked about
    builds = graphene.List(graphene.NonNull(Build), required=True)

    # resolvers
    @staticmethod
    def resolve_builds(store, info, **kwds):
        """
        Describe the preparation of every dataset a client has asked about
        """
        # the store keeps the records
        return store.builds()


# end of file
