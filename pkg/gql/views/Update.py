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
class Update(graphene.Mutation):
    """
    Remove a view
    """

    # inputs
    class Arguments:
        # the update context
        viewport = graphene.Int(required=True)
        reader = graphene.String(required=False)
        dataset = graphene.String(required=False)
        channel = graphene.String(required=False)

    # the result is the new list of views
    view = graphene.Field(View)

    # the range controller mutator
    @staticmethod
    def mutate(root, info, viewport, reader, dataset, channel):
        """
        Remove a reader from the pile
        """
        # get the store
        store = info.context["store"]
        # ask it to split the view
        view = store.updateView(
            viewport=viewport, reader=reader, dataset=dataset, channel=channel
        )
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
