# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# response types
from .Measure import Measure


# remove an anchor from the pile
class MeasureAnchorRemove(graphene.Mutation):
    """
    Remove an anchor from the pile
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)
        anchor = graphene.Int(required=True)

    # the result is the updated view
    measures = graphene.List(Measure)

    # the mutator
    @staticmethod
    def mutate(root, info, viewport, anchor):
        """
        Toggle the anchor selection in single node mode
        """
        # get the store
        store = info.context["store"]
        # ask it to toggle the selection
        measures = store.measureAnchorRemove(viewport=viewport, anchor=anchor)
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
