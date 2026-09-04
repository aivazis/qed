# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the request payload
from .ViewRangeResizeInput import ViewRangeResizeInput

# the result types
from ..views.View import View
from .RangeController import RangeController


# resize a range controller
class ViewRangeResize(graphene.Mutation):
    """
    Set the display bounds of a range controller by hand; the bounds must leave the picks in
    place, so the rendered pixels never change, and the edit pins the controller
    """

    # inputs
    class Arguments:
        # the request payload
        input = ViewRangeResizeInput(required=True)

    # the result is the view, whose session token is unchanged since no pixels moved
    view = graphene.Field(View)
    # and the resized range controller
    controller = graphene.Field(RangeController)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Resize the controller named in {input}
        """
        # unpack the payload
        viewport = input["viewport"]
        channelName = input["channel"]
        controllerName = input["controller"]
        # grab the store
        store = info.context["store"]
        # ask it to resize the controller; a refused extent surfaces as a failed mutation
        view, controller = store.vizResizeController(
            viewport=viewport,
            channel=channelName,
            name=controllerName,
            min=input["min"],
            max=input["max"],
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
