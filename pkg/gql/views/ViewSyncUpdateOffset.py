# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewSyncUpdateOffsetInput import ViewSyncUpdateOffsetInput

# the result types
from .ViewSync import ViewSync


# update the sync scroll offset
class ViewSyncUpdateOffset(graphene.Mutation):
    """
    Update the sync scroll offset
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewSyncUpdateOffsetInput(required=True)

    # the result is the updated sync state
    sync = graphene.Field(ViewSync)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Update the sync scroll offset of {input.viewport}
        """
        # get the store
        store = info.context["store"]
        # set the offset aspect
        sync = store.syncSetAspect(
            viewport=input.viewport, aspect="offsets", value=(input.x, input.y)
        )
        # form the mutation resolution context
        context = {"sync": sync}
        # and resolve the mutation
        return context


# end of file
