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
class MeasureAnchorPlace(graphene.Mutation):
    """
    Toggle the anchor selection in single node mode
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)
        handle = graphene.Int(required=True)
        x = graphene.Int(required=True)
        y = graphene.Int(required=True)

    # the result is the updated view
    measure = graphene.Field(Measure)

    # the mutator
    @staticmethod
    def mutate(root, info, viewport, handle, x, y):
        """
        Toggle the anchor selection in single node mode
        """
        # get the store
        store = info.context["store"]
        # ask it to toggle the selection
        measure = store.measureAnchorPlace(viewport=viewport, handle=handle, x=x, y=y)
        # form the mutation resolution context
        context = {"measure": measure}
        # and resolve the mutation
        return context


# end of file
