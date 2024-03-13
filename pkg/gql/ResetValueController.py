# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import uuid

# the input payload
from .ValueControllerInput import ValueControllerInput

# the result types
from .ValueController import ValueController


# reset the value of a controller
class ResetValueController(graphene.Mutation):
    """
    Reset the value of a controller
    """

    # inputs
    class Arguments:
        # the reset context
        controller = ValueControllerInput(required=True)

    # the result is always a value controller
    controller = graphene.Field(ValueController)

    # the value controller mutator
    def mutate(root, info, controller):
        """
        Reset the value of a controller
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
