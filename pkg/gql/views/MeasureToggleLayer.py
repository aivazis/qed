# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene
import journal


# the result types
from .ViewMeasure import ViewMeasure


# remove a view from the pile
class MeasureToggleLayer(graphene.Mutation):
    """
    Toggle a reader's participation in the measure layer
    """

    # inputs
    class Arguments:
        # the update context
        viewport = graphene.Int(required=True)
        reader = graphene.String(required=True)

    # the result is the new measure layer object
    measures = graphene.List(ViewMeasure)

    # the range controller mutator
    @staticmethod
    def mutate(root, info, viewport, reader):
        """
        Remove a reader from the pile
        """
        # get the store
        store = info.context["store"]
        # ask it for the measure layer of the dataset view
        measures = store.toggleMeasure(viewport=viewport, source=reader)
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
