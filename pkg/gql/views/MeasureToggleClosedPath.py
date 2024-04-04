# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# response types
from .Measure import Measure


# toggle the closed path flag
class MeasureToggleClosedPath(graphene.Mutation):
    """
    Split in two the leg that starts at an anchor
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)

    # the result is the updated view
    measure = graphene.Field(Measure)

    # the mutator
    @staticmethod
    def mutate(root, info, viewport):
        """
        Toggle the closed path flag
        """
        # get the store
        store = info.context["store"]
        # ask it to toggle the selection
        measure = store.measureToggleClosedPath(viewport=viewport)
        # form the mutation resolution context
        context = {"measure": measure}
        # and resolve the mutation
        return context


# end of file
