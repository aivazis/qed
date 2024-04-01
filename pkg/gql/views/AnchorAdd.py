# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# the result types
from .Measure import Measure


# add an anchor to the path
class AnchorAdd(graphene.Mutation):
    """
    Remove a view
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)
        x = graphene.Int(required=True)
        y = graphene.Int(required=True)
        index = graphene.Int(required=False)

    # the result is the updated view
    measure = graphene.Field(Measure)

    # the range controller mutator
    @staticmethod
    def mutate(root, info, viewport, x, y, index):
        """
        Remove a reader from the pile
        """
        # get the store
        store = info.context["store"]
        # ask it to add an anchor to the path
        measure = store.measureAddAnchor(viewport=viewport, x=x, y=y, index=index)
        # form the mutation resolution context
        context = {"measure": measure}
        # and resolve the mutation
        return context


# end of file
