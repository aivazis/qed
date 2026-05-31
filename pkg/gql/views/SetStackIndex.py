# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the result types
from .View import View


# pin or clear a stack member for a viewport
class SetStackIndex(graphene.Mutation):
    """
    Pin a stack member, or clear the pin to return to the collective aggregate view
    """

    # inputs
    class Arguments:
        # the viewport
        viewport = graphene.Int(required=True)
        # the stack to act on
        source = graphene.String(required=True)
        # the member to pin; omit or pass null to clear the pin
        index = graphene.Int(required=False)

    # the result is the updated view
    view = graphene.Field(View)

    # the mutator
    @staticmethod
    def mutate(root, info, viewport, source, index=None):
        """
        Pin the stack member {index} of {source} in {viewport}, or clear it when {index} is None
        """
        # get the store
        store = info.context["store"]
        # ask it to pin or clear the member
        view = store.setStackIndex(viewport=viewport, source=source, index=index)
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
