# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene
import uuid

# the input payload
from .ValueControllerResetInput import ValueControllerResetInput

# the result types
from .views.View import View
from .ValueController import ValueController


# reset the value of a controller
class ResetValueController(graphene.Mutation):
    """
    Reset the value of a controller
    """

    # inputs
    class Arguments:
        # the reset context
        controller = ValueControllerResetInput(required=True)

    # the result is a view with a new session token
    view = graphene.Field(View)
    # and a range controller
    controller = graphene.Field(ValueController)

    # the value controller mutator
    @staticmethod
    def mutate(root, info, controller):
        """
        Reset the value of a controller
        """
        # unpack the input payload
        viewport = controller["viewport"]
        channelName = controller["channel"]
        controllerName = controller["controller"]

        # build the resolution context
        # grab the store
        store = info.context["store"]
        # ask it to update the controller
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
