# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewCollapseInput import ViewCollapseInput

# the result types
from .View import View


# remove a view from the pile
class ViewCollapse(graphene.Mutation):
    """
    Remove a view
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewCollapseInput(required=True)

    # the result is the view that was removed from the pile
    view = graphene.Field(View)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Collapse the view in {input.viewport}
        """
        # get the store
        store = info.context["store"]
        # ask it to collapse the view
        view = store.collapseViewport(viewport=input.viewport)
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
