# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the payload
from .PlaygroundProjectionSetInput import PlaygroundProjectionSetInput

# the result
from .PlaygroundView import PlaygroundView


# change the projection of the playground
class PlaygroundProjectionSet(graphene.Mutation):
    """
    Change how the diagram of the playground is projected, for every client
    """

    # inputs
    class Arguments:
        # the payload
        input = PlaygroundProjectionSetInput(required=True)

    # the result is how the playground is looked at
    view = graphene.Field(PlaygroundView)

    # the range of possible mutations
    @staticmethod
    def mutate(root, info, input):
        """
        Change how the diagram of the playground is projected
        """
        # get the store
        store = info.context["store"]
        # ask it to make the change
        view = store.playgroundProjectionSet(
            kind=input.kind, azimuth=input.azimuth, below=input.below
        )
        # and hand off the view
        return {"view": view}


# end of file
