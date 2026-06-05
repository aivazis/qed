# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewSplitInput import ViewSplitInput

# the result types
from .View import View


# split a viewport in two
class ViewSplit(graphene.Mutation):
    """
    Split the current viewport
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewSplitInput(required=True)

    # the result is the new view that was added to the pile
    view = graphene.Field(View)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Split the view in {input.viewport}
        """
        # get the store
        store = info.context["store"]
        # ask it to split the view
        view = store.splitViewport(viewport=input.viewport)
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
