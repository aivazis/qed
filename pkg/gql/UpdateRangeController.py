# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene
# the input payload
from .RangeControllerInput import RangeControllerInput
# the result types
from .RangeController import RangeController


# update the range of a controller
class UpdateRangeController(graphene.Mutation):
    """
    Update the value range of a ranged controller
    """


    # inputs
    class Arguments:
        # the update context
        range = RangeControllerInput(required=True)


    # the result is always a range controller
    controller = graphene.Field(RangeController)


    def mutate(root, info, range):
        """
        Update the range of a controller
        """
        # assemble the resolution context
        # unpack the input payload
        dataset = range["dataset"]
        channel = range["channel"]
        slot = range["slot"]
        low = range["low"]
        high = range["high"]

        # build the resolution context
        # grab the panel
        panel = info.context["panel"]
        # get the nameserver
        ns = panel.pyre_nameserver
        # ask it for the controller
        controller = ns[slot]

        # update
        controller.low = low
        controller.high = high

        # and use the result to resolve the mutation
        return {"controller": controller}


# end of file
