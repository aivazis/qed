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
class SelectReader(graphene.Mutation):
    """
    Place a reader in a viewport
    """

    # inputs
    class Arguments:
        # the update context
        viewport = graphene.Int(required=True)
        reader = graphene.String(required=False)

    # the result is the updated view
    view = graphene.Field(View)

    # the range controller mutator
    @staticmethod
    def mutate(root, info, viewport, reader):
        """
        Remove a reader from the pile
        """
        # get the store
        store = info.context["store"]
        # ask it to set the reader of the {viewport}
        view = store.selectReader(viewport=viewport, name=reader)
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
