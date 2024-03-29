# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene
import uuid

# the input payload
from .RangeControllerRangeInput import RangeControllerRangeInput

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
        range = RangeControllerRangeInput(required=True)

    # the result is always a range controller
    controller = graphene.Field(RangeController)

    # the range controller mutator
    @staticmethod
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
        changed = controller.updateRange(low=low, high=high)
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
