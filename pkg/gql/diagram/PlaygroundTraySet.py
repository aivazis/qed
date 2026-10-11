# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the payload
from .PlaygroundTraySetInput import PlaygroundTraySetInput

# the result
from .PlaygroundView import PlaygroundView


# open or close a tray of the playground
class PlaygroundTraySet(graphene.Mutation):
    """
    Open or close a tray of the playground's panel, for every client
    """

    # inputs
    class Arguments:
        # the payload
        input = PlaygroundTraySetInput(required=True)

    # the result is how the playground is looked at
    view = graphene.Field(PlaygroundView)

    # the range of possible mutations
    @staticmethod
    def mutate(root, info, input):
        """
        Open or close a tray of the playground's panel
        """
        # get the store
        store = info.context["store"]
        # ask it to make the change
        view = store.playgroundTraySet(tray=input.tray, expanded=input.expanded)
        # and hand off the view
        return {"view": view}


# end of file
