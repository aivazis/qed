# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import uuid

# the input payload
from .ValueControllerValueInput import ValueControllerValueInput

# the result types
from .ValueController import ValueController


# update the value of a controller
class UpdateValueController(graphene.Mutation):
    """
    Update the value of a controller
    """

    # inputs
    class Arguments:
        # the update context
        value = ValueControllerValueInput(required=True)

    # the result is always a value controller
    controller = graphene.Field(ValueController)

    # the value controller mutator
    @staticmethod
    def mutate(root, info, value):
        """
        Update the value of a controller
        """
        # unpack the input payload
        dataset = value["dataset"]
        channel = value["channel"]
        slot = value["slot"]
        newValue = value["value"]

        # build the resolution context
        # grab the store
        store = info.context["store"]

        # get the dataset
        dataset = store.dataset(name=dataset)
        # ask it for the channel
        channel = dataset.channel(name=channel)
        # ask it for its controller
        controller = getattr(channel, slot)
        # and the controller metadata
        trait = channel.pyre_trait(alias=slot)

        # update
        changed = controller.updateValue(value=newValue)
        # and refresh the session key, if necessary
        session = uuid.uuid1() if changed else controller.pyre_id

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
