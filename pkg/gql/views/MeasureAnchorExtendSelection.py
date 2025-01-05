# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene
import journal


# the result types
from .Measure import Measure


# extend the current anchor selection to a given anchor index
class MeasureAnchorExtendSelection(graphene.Mutation):
    """
    Extend the anchor selection to a given anchor index
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)
        index = graphene.Int(required=False)

    # the result is the updated view
    measures = graphene.List(Measure)

    # the mutator
    @staticmethod
    def mutate(root, info, viewport, index):
        """
        Extend the anchor selection to a given anchor index
        """
        # get the store
        store = info.context["store"]
        # ask it to add an anchor to the path
        measures = store.measureAnchorExtendSelection(viewport=viewport, index=index)
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
