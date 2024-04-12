# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import journal


# the result types
from .View import View


# remove a view from the pile
class SyncToggleViewport(graphene.Mutation):
    """
    Toggle the state of the measure layer of a dataset
    """

    # inputs
    class Arguments:
        # the update context
        viewport = graphene.Int(required=True)
        aspect = graphene.String(required=True)

    # the result is the new measure layer object
    view = graphene.Field(View)

    # the range controller mutator
    @staticmethod
    def mutate(root, info, viewport, aspect):
        """
        Remove a reader from the pile
        """
        # get the store
        store = info.context["store"]
        # ask it for the measure layer of the dataset view
        view = store.syncToggleViewport(viewport=viewport, aspect=aspect)
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
