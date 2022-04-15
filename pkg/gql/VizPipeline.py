# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene
# individual controls
from .Controller import Controller


# a representation of the visualization pipeline for a specific {channel} of a {dataset}
class VizPipeline(graphene.ObjectType):
    """
    The value of a dataset sample
    """

    # fields
    dataset = graphene.ID()
    channel = graphene.ID()
    controllers = graphene.List(Controller)


    # resolvers
    def resolve_dataset(context, info, **kwds):
        """
        Extract the name of the dataset
        """
        # get the dataset
        dataset = context["dataset"]
        # and return its name
        return dataset.pyre_name


    def resolve_channel(context, info, **kwds):
        """
        Extract the name of the channel
        """
        # get the dataset
        channel = context["channel"]
        # and return its name
        return channel.tag


    def resolve_controllers(context, info, **kwds):
        """
        Extract the necessary controllers from the dataset channel
        """
        # get the channel
        channel = context["channel"]
        # and ask it for its controllers
        for controller, trait in channel.controllers():
            # pack into a resolution context
            context = {
                "controller": controller,
                "trait": trait,
            }
            # and resolve it
            yield context
        # all done
        return


# end of file
