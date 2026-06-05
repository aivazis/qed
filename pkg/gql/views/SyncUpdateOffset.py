# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene
import journal


# the result types
from .ViewSync import ViewSync


# remove a view from the pile
class SyncUpdateOffset(graphene.Mutation):
    """
    Update the sync scroll offset
    """

    # inputs
    class Arguments:
        # the update context
        viewport = graphene.Int(required=True)
        x = graphene.Int(required=True)
        y = graphene.Int(required=True)

    # the result is the new measure layer object
    sync = graphene.Field(ViewSync)

    # the range controller mutator
    @staticmethod
    def mutate(root, info, viewport, x, y):
        """
        Remove a reader from the pile
        """
        # get the store
        store = info.context["store"]
        # ask it for the measure layer of the dataset view
        sync = store.syncSetAspect(viewport=viewport, aspect="offsets", value=(x, y))
        # form the mutation resolution context
        context = {"sync": sync}
        # and resolve the mutation
        return context


# end of file
