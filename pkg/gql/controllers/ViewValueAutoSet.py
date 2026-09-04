# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewValueAutoSetInput import ViewValueAutoSetInput

# the result types
from ..views.View import View
from .ValueController import ValueController


# set the auto flag of a value controller
class ViewValueAutoSet(graphene.Mutation):
    """
    Pin a value controller, or release it to follow the data statistics; a released controller
    stretches its display bounds to accommodate the statistics accumulated so far, but its picks
    never move, so the rendered pixels are unchanged
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewValueAutoSetInput(required=True)

    # the result is the view, whose session token is unchanged since no pixels moved
    view = graphene.Field(View)
    # and the adjusted value controller
    controller = graphene.Field(ValueController)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Set the auto flag of the controller named in {input}
        """
        # unpack the payload
        viewport = input["viewport"]
        channelName = input["channel"]
        controllerName = input["controller"]
        # grab the store
        store = info.context["store"]
        # ask it to adjust the controller
        view, controller = store.vizSetControllerAuto(
            viewport=viewport,
            channel=channelName,
            name=controllerName,
            auto=input["auto"],
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
