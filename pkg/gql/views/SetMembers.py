# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the result types
from .View import View


# set the per-member participation mask of a stack for a viewport
class SetMembers(graphene.Mutation):
    """
    Set which members of a stack participate in its aggregate views
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)
        # the stack to act on
        source = graphene.String(required=True)
        # the per-member participation mask, aligned to the stack's member order
        members = graphene.List(graphene.NonNull(graphene.Boolean), required=True)

    # the result is the updated view
    view = graphene.Field(View)

    # the mutator
    @staticmethod
    def mutate(root, info, viewport, source, members):
        """
        Set the participation {members} of the stack {source} in {viewport}
        """
        # get the store
        store = info.context["store"]
        # ask it to set the mask
        view = store.setMembers(viewport=viewport, source=source, members=members)
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
