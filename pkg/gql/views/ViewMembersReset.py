# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewMembersResetInput import ViewMembersResetInput

# the result types
from .View import View


# restore a stack to its default participation mask for a viewport
class ViewMembersReset(graphene.Mutation):
    """
    Restore a stack's membership to the default it was primed with
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewMembersResetInput(required=True)

    # the result is the updated view
    view = graphene.Field(View)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Restore the default membership of the stack {input.reader} in {input.viewport}
        """
        # get the store
        store = info.context["store"]
        # ask it to reset the mask
        view = store.resetMembers(viewport=input.viewport, source=input.reader)
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
