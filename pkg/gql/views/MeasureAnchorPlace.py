# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene
import journal


# response types
from .ViewMeasure import ViewMeasure


# toggle the current anchor selection in single node mode
class MeasureAnchorPlace(graphene.Mutation):
    """
    Place a measure handle at a pixel
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)
        handle = graphene.Int(required=True)
        x = graphene.Int(required=True)
        y = graphene.Int(required=True)

    # the result is the updated view
    measures = graphene.List(ViewMeasure)

    # the mutator
    @staticmethod
    def mutate(root, info, viewport, handle, x, y):
        """
        Place a measure handle at a pixel
        """
        # get the store
        store = info.context["store"]
        # ask it to toggle the selection
        measures = store.measureAnchorPlace(viewport=viewport, handle=handle, x=x, y=y)
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
