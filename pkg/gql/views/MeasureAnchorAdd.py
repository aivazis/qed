# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene
import journal


# the result types
from .ViewMeasure import ViewMeasure


# add an anchor to the path
class MeasureAnchorAdd(graphene.Mutation):
    """
    Add an anchor to the measure path
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)
        x = graphene.Int(required=True)
        y = graphene.Int(required=True)
        index = graphene.Int(required=False)

    # the result is the updated view
    measures = graphene.List(ViewMeasure)

    # the range controller mutator
    @staticmethod
    def mutate(root, info, viewport, x, y, index):
        """
        Remove a reader from the pile
        """
        # get the store
        store = info.context["store"]
        # ask it to add an anchor to the path
        measures = store.measureAddAnchor(viewport=viewport, x=x, y=y, index=index)
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
