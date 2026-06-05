# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewSyncResetInput import ViewSyncResetInput

# the result types
from .ViewSync import ViewSync


# reset the sync state
class ViewSyncReset(graphene.Mutation):
    """
    Reset the sync state back to its persisted value
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewSyncResetInput(required=True)

    # the result is the updated sync state
    sync = graphene.Field(ViewSync)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Reset the sync state of {input.viewport}
        """
        # get the store
        store = info.context["store"]
        # reset the sync state
        sync = store.syncReset(viewport=input.viewport)
        # form the mutation resolution context
        context = {"sync": sync}
        # and resolve the mutation
        return context


# end of file
