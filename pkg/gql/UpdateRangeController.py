# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene
# the input payload
from .RangeControllerInput import RangeControllerInput


# update the range of a controller
class UpdateRangeController(graphene.Mutation):
    """
    Update the value range of a ranged controller
    """


    # inputs
    class Arguments:
        # the update context
        range = RangeControllerInput(required=True)


    # the updated fields
    min = graphene.Float(required=True)
    max = graphene.Float(required=True)
    low = graphene.Float(required=True)
    high = graphene.Float(required=True)


    # the mutator
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
        # grab the plexus
        panel = info.context["panel"]
        # resolve the dataset
        dataset = panel.dataset(name=dataset)
        # and the channel
        channel = dataset.channel(name=channel)


        print(f"channel: {channel.pyre_name}")
        print(f"  slot: {slot}")
        print(f"  new low: {low}")
        print(f"  new high: {high}")


        # resolve
        return


# end of file
