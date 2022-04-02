# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene
# the pixel values as represented by each channel
from .ChannelRep import ChannelRep


# a sample from a dataset
class Sample(graphene.ObjectType):
    """
    The value of a dataset sample
    """

    # fields
    pixel = graphene.List(graphene.Int)
    value = graphene.List(ChannelRep)


    # resolvers
    def resolve_value(context, info, **kwds):
        """
        Get the value of a dataset at the specified location
        """
        # unpack my context
        dataset = context["dataset"]
        points = [(context["line"], context["sample"])]
        # ask the dataset for a profile over my point
        profile = dataset.profile(points=points)
        # unpack the pixel value out of the single entry
        _, _, pixel = profile[0]

        # get the dataset channels
        channels = dataset.channels

        # go through the summary channels
        for channel in dataset.cell.summary:
            # build the representations
            yield {
                "channel": channel,
                "reps": channels[channel].project(pixel),
            }

        # all done
        return


    def resolve_pixel(context, info, **kwds):
        """
        Get the value of a dataset at the specified location
        """
        # all done
        return [context["line"], context["sample"]]


# end of file
