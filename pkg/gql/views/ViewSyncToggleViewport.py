# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewSyncToggleViewportInput import ViewSyncToggleViewportInput

# the result types
from .View import View


# toggle a sync aspect for a single viewport
class ViewSyncToggleViewport(graphene.Mutation):
    """
    Toggle a sync aspect for a single viewport
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewSyncToggleViewportInput(required=True)

    # the result is the updated view
    view = graphene.Field(View)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Toggle the {input.aspect} sync aspect of {input.viewport}
        """
        # get the store
        store = info.context["store"]
        # toggle the aspect for the viewport
        view = store.syncToggleViewport(viewport=input.viewport, aspect=input.aspect)
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
