# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewLookAtInput import ViewLookAtInput

# the result types
from .ViewCenter import ViewCenter


# set the look-at center
class ViewLookAt(graphene.Mutation):
    """
    Set the source pixel that sits at the center of the viewport
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewLookAtInput(required=True)

    # the result is the affected center state
    center = graphene.Field(ViewCenter)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Set the look-at center for {input.viewport}
        """
        # get the store
        store = info.context["store"]
        # set the center
        center = store.lookAt(
            viewport=input.viewport,
            row=input.row,
            col=input.col,
        )
        # form the mutation resolution context
        context = {"center": center}
        # and resolve the mutation
        return context


# end of file
