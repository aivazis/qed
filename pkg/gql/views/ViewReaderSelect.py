# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewReaderSelectInput import ViewReaderSelectInput

# the result types
from .View import View


# place a reader in a viewport
class ViewReaderSelect(graphene.Mutation):
    """
    Place a reader in a viewport
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewReaderSelectInput(required=True)

    # the result is the updated view
    view = graphene.Field(View)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Place the reader {input.reader} in {input.viewport}
        """
        # get the store
        store = info.context["store"]
        # ask it to set the reader of the {viewport}
        view = store.selectSource(viewport=input.viewport, name=input.reader)
        # form the mutation resolution context
        context = {"view": view}
        # and resolve the mutation
        return context


# end of file
