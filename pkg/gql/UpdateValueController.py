# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene
import uuid

# the input payload
from .ValueControllerUpdateInput import ValueControllerUpdateInput

# the result types
from .views.View import View
from .ValueController import ValueController


# update the value of a controller
class UpdateValueController(graphene.Mutation):
    """
    Update the value of a controller
    """

    # inputs
    class Arguments:
        # the update context
        value = ValueControllerUpdateInput(required=True)

    # the result is a view with a new session token
    view = graphene.Field(View)
    # and a range controller
    controller = graphene.Field(ValueController)

    # the value controller mutator
    @staticmethod
    def mutate(root, info, value):
        """
        Update the value of a controller
        """
        # unpack the input payload
        viewport = value["viewport"]
        channelName = value["channel"]
        controllerName = value["controller"]
        configuration = {
            "min": value["min"],
            "value": value["value"],
            "max": value["max"],
        }

        # build the resolution context
        # grab the store
        store = info.context["store"]

        # build the resolution context
        # grab the store
        store = info.context["store"]
        # ask it to update the controller
        view, controller = store.vizUpdateController(
            viewport=viewport,
            channel=channelName,
            name=controllerName,
            configuration=configuration,
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
