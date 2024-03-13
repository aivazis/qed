# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import uuid

# the input payload
from .RangeControllerInput import RangeControllerInput

# the result types
from .RangeController import RangeController


# reset the range of a controller
class ResetRangeController(graphene.Mutation):
    """
    Reset the value range of a ranged controller
    """

    # inputs
    class Arguments:
        # the reset context
        controller = RangeControllerInput(required=True)

    # the result is always a range controller
    controller = graphene.Field(RangeController)

    # the range controller mutator
    def mutate(root, info, controller):
        """
        Reset the range of a controller
        """
        # unpack the input payload
        datasetName = controller["dataset"]
        channelName = controller["channel"]
        slotName = controller["slot"]

        # get the configuration store
        store = info.context["store"]

        # form the channel name
        name = f"{datasetName}.{channelName}"
        # get the channel view
        view = store.channel(name=name)
        # get the controller configuration
        configuration = view.vizConfiguration[slotName]

        # get the dataset
        dataset = store.dataset(name=datasetName)
        # get the channel
        channel = dataset.channels[channelName]
        # retrieve the controller
        controller = getattr(channel, slotName)
        # and its metadata
        trait = channel.pyre_trait(alias=slotName)

        # go through the stored state
        for attr, value in configuration.items():
            # and apply it to the controller
            setattr(controller, attr, value)

        # refresh the session key
        session = uuid.uuid1()

        # build the context for the response resolution
        context = {
            "controller": {
                "controller": controller,
                "trait": trait,
                "session": session,
            }
        }

        # and use the result to resolve the mutation
        return context


# end of file
