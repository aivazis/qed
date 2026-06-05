# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene
import journal


# response types
from .ViewMeasure import ViewMeasure


# toggle the closed path flag
class MeasureToggleClosedPath(graphene.Mutation):
    """
    Toggle whether the measure path is closed
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)

    # the result is the updated view
    measures = graphene.List(ViewMeasure)

    # the mutator
    @staticmethod
    def mutate(root, info, viewport):
        """
        Toggle the closed path flag
        """
        # get the store
        store = info.context["store"]
        # ask it to toggle the selection
        measures = store.measureToggleClosedPath(viewport=viewport)
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
