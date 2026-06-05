# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewRangeResetInput import ViewRangeResetInput

# the result types
from ..views.View import View
from .RangeController import RangeController


# reset a ranged controller
class ViewRangeReset(graphene.Mutation):
    """
    Reset the value range of a ranged controller
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewRangeResetInput(required=True)

    # the result is a view with a new session token
    view = graphene.Field(View)
    # and the reset range controller
    controller = graphene.Field(RangeController)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Reset the range of the controller named in {input}
        """
        # unpack the payload
        viewport = input["viewport"]
        channelName = input["channel"]
        controllerName = input["controller"]
        # grab the store
        store = info.context["store"]
        # ask it to reset the controller
        view, controller = store.vizResetController(
            viewport=viewport,
            channel=channelName,
            name=controllerName,
        )
        # build the resolution context
        context = {
            "view": view,
            "controller": {
                "controller": controller,
            },
        }
        # and use the result to resolve the mutation
        return context


# end of file
