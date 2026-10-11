# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the payload
from .PlaygroundCameraSetInput import PlaygroundCameraSetInput

# the result
from .PlaygroundView import PlaygroundView


# point the cameras on the playground
class PlaygroundCameraSet(graphene.Mutation):
    """
    Point every client's camera at a place on the playground
    """

    # inputs
    class Arguments:
        # the payload
        input = PlaygroundCameraSetInput(required=True)

    # the result is how the playground is looked at
    view = graphene.Field(PlaygroundView)

    # the range of possible mutations
    @staticmethod
    def mutate(root, info, input):
        """
        Point every client's camera at a place on the playground
        """
        # get the store
        store = info.context["store"]
        # ask it to make the change
        view = store.playgroundCameraSet(x=input.x, y=input.y, z=input.z)
        # and hand off the view
        return {"view": view}


# end of file
