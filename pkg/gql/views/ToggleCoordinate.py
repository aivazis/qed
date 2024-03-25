# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# the request payload
from .ViewSelectorInput import ViewSelectorInput

# the result types
from .View import View


# remove a view from the pile
class ToggleCoordinate(graphene.Mutation):
    """
    Remove a view
    """

    # inputs
    class Arguments:
        # the update context
        selection = ViewSelectorInput(required=True)

    # the result is the updated view
    view = graphene.Field(View)

    # the range controller mutator
    @staticmethod
    def mutate(root, info, selection):
        """
        Remove a reader from the pile
        """
        # unpack the selector
        viewport = selection.viewport
        reader = selection.reader
        axis = selection.selector
        coordinate = selection.value
        # get the store
        store = info.context["store"]
        # ask it to set the reader of the {viewport}
        view = store.toggleCoordinate(
            viewport=viewport, reader=reader, axis=axis, coordinate=coordinate
        )
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
