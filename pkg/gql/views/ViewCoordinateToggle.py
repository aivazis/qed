# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewCoordinateToggleInput import ViewCoordinateToggleInput

# the result types
from .View import View


# toggle a coordinate value in a view's dataset selection
class ViewCoordinateToggle(graphene.Mutation):
    """
    Toggle a coordinate value in a view's dataset selection
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewCoordinateToggleInput(required=True)

    # the result is the updated view
    view = graphene.Field(View)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Toggle {input.value} for the {input.selector} axis of {input.reader} in {input.viewport}
        """
        # get the store
        store = info.context["store"]
        # ask it to toggle the coordinate
        view = store.toggleCoordinate(
            viewport=input.viewport,
            source=input.reader,
            axis=input.selector,
            coordinate=input.value,
        )
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
