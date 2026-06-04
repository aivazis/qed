# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the result types
from .View import View


# restore a stack to its default participation mask for a viewport
class ResetMembers(graphene.Mutation):
    """
    Restore a stack's membership to the default it was primed with
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)
        # the stack to act on
        source = graphene.String(required=True)

    # the result is the updated view
    view = graphene.Field(View)

    # the mutator
    @staticmethod
    def mutate(root, info, viewport, source):
        """
        Restore the default membership of the stack {source} in {viewport}
        """
        # get the store
        store = info.context["store"]
        # ask it to reset the mask
        view = store.resetMembers(viewport=viewport, source=source)
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
