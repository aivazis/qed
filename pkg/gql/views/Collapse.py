# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene
import journal


# the result types
from .View import View


# remove a view from the pile
class Collapse(graphene.Mutation):
    """
    Remove a view
    """

    # inputs
    class Arguments:
        # the update context
        viewport = graphene.Int(required=True)

    # the result is view that was removed from the pile
    view = graphene.Field(View)

    # the range controller mutator
    @staticmethod
    def mutate(root, info, viewport):
        """
        Remove a reader from the pile
        """
        # get the store
        store = info.context["store"]
        # ask it to collapse the view
        view = store.collapseViewport(viewport=viewport)
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
