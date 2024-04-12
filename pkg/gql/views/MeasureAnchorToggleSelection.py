# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# response types
from .Measure import Measure


# toggle the current anchor selection in single node mode
class MeasureAnchorToggleSelection(graphene.Mutation):
    """
    Toggle the anchor selection in single node mode
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
        Toggle the anchor selection in single node mode
        """
        # get the store
        store = info.context["store"]
        # ask it to toggle the selection
        measures = store.measureAnchorToggleSelection(viewport=viewport, index=index)
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
