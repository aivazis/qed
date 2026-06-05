# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewValueResetInput import ViewValueResetInput

# the result types
from ..views.View import View
from .ValueController import ValueController


# reset the value of a controller
class ViewValueReset(graphene.Mutation):
    """
    Reset the value of a controller
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewValueResetInput(required=True)

    # the result is a view with a new session token
    view = graphene.Field(View)
    # and the reset value controller
    controller = graphene.Field(ValueController)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Reset the value of the controller named in {input}
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
