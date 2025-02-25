# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene
import journal


# the result types
from .Measure import Measure


# add an anchor to the path
class MeasureMakeBox(graphene.Mutation):
    """
    Remove a view
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)

    # the result is the updated view
    measures = graphene.List(Measure)

    # the range controller mutator
    @staticmethod
    def mutate(root, info, viewport):
        """
        Remove a reader from the pile
        """
        # get the store
        store = info.context["store"]
        # ask it to add an anchor to the path
        measures = store.measureMakeBox(viewport=viewport)
        # form the mutation resolution context
        context = {"measures": measures}
        # and resolve the mutation
        return context


# end of file
