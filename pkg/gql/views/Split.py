# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# the result types
from .View import View


# remove a view from the pile
class Split(graphene.Mutation):
    """
    Split the current viewport
    """

    # inputs
    class Arguments:
        # the update context
        viewport = graphene.Int(required=True)

    # the result is the new view that was added in the pile
    view = graphene.Field(View)

    # the range controller mutator
    @staticmethod
    def mutate(root, info, viewport):
        """
        Remove a reader from the pile
        """
        # get the store
        store = info.context["store"]
        # ask it to split the view
        view = store.splitViewport(viewport=viewport)
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
