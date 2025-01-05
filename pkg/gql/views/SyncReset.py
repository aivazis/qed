# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene
import journal


# response types
from .Sync import Sync


# reset the sync state
class SyncReset(graphene.Mutation):
    """
    Reset the sync state back to its persisted value
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)

    # the result is the updated view
    sync = graphene.Field(Sync)

    # the mutator
    @staticmethod
    def mutate(root, info, viewport):
        """
        Reset the sync state
        """
        # get the store
        store = info.context["store"]
        # ask it to toggle the selection
        sync = store.syncReset(viewport=viewport)
        # form the mutation resolution context
        context = {"sync": sync}
        # and resolve the mutation
        return context


# end of file
