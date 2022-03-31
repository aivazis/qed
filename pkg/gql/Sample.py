# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene
# the pixel values as represenged by each channel
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
        # ask each {dataset} channel to represent the pixels
        reps = [
            {"channel": name, "rep": channel.rep(pixel)}
            for name, channel in dataset.channels.items()
        ]
        # and send them off
        return reps


    def resolve_pixel(context, info, **kwds):
        """
        Get the value of a dataset at the specified location
        """
        # all done
        return [context["line"], context["sample"]]


# end of file
