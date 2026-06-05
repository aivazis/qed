# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewSyncToggleAllInput import ViewSyncToggleAllInput

# the result types
from .View import View


# toggle a sync aspect across all viewports
class ViewSyncToggleAll(graphene.Mutation):
    """
    Toggle a sync aspect across all viewports
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewSyncToggleAllInput(required=True)

    # the result is the affected views
    views = graphene.List(View)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Toggle the {input.aspect} sync aspect across all viewports
        """
        # get the store
        store = info.context["store"]
        # toggle the aspect everywhere
        views = store.syncToggleAll(viewport=input.viewport, aspect=input.aspect)
        # form the mutation resolution context
        context = {"views": views}
        # and resolve the mutation
        return context


# end of file
