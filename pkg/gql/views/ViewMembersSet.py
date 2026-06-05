# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewMembersSetInput import ViewMembersSetInput

# the result types
from .View import View


# set the per-member participation mask of a stack for a viewport
class ViewMembersSet(graphene.Mutation):
    """
    Set which members of a stack participate in its aggregate views
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewMembersSetInput(required=True)

    # the result is the updated view
    view = graphene.Field(View)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Set the participation {input.members} of the stack {input.reader} in {input.viewport}
        """
        # get the store
        store = info.context["store"]
        # ask it to set the mask
        view = store.setMembers(
            viewport=input.viewport, source=input.reader, members=input.members
        )
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
