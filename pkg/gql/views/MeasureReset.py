# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# response types
from .Measure import Measure


# reset the measure state
class MeasureReset(graphene.Mutation):
    """
    Reset the measure state back to its persisted value
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
        Reset the measure state
        """
        # get the store
        store = info.context["store"]
        # ask it to toggle the selection
        measure = store.measureReset(viewport=viewport)
        # form the mutation resolution context
        context = {"measure": measure}
        # and resolve the mutation
        return context


# end of file
