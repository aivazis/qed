# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewEngineSetInput import ViewEngineSetInput

# the result
from .View import View


# pick the engine that draws the tiles of a view
class ViewEngineSet(graphene.Mutation):
    """
    Pick the engine that draws the tiles of a view: the pipeline of its channel's recipe, or the
    fused iterators
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewEngineSetInput(required=True)

    # the result is the affected views
    views = graphene.List(View)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Draw the tiles of {input.viewport} with {input.engine}
        """
        # get the store
        store = info.context["store"]
        # ask it to set the engine
        views = store.engineSet(viewport=input.viewport, engine=input.engine)
        # form the mutation resolution context
        context = {"views": views}
        # and resolve the mutation
        return context


# end of file
