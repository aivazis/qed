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
        # unpack the input payload
        dataset = range["dataset"]
        channel = range["channel"]
        slot = range["slot"]
        low = range["low"]
        high = range["high"]

        # build the resolution context
        # grab the panel
        panel = info.context["panel"]

        # get the dataset
        dataset = panel.dataset(name=dataset)
        # ask it for the channel
        channel = dataset.channel(name=channel)
        # ask it for its controller
        controller = getattr(channel, slot)
        # and the controller metadata
        trait = channel.pyre_trait(alias=slot)

        # update
        controller.low = low
        controller.high = high

        # build the context for the response resolution
        context = {
            "controller" : {
                "controller": controller,
                "trait": trait,
            }
        }

        # and use the result to resolve the mutation
        return context


# end of file
