# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


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
        line = context["line"]
        sample = context["sample"]

        # ask the dataset for the pixel value projected on its favorite channels
        for channel, reps in dataset.peek(pixel=(line, sample)):
            # and assemble a resolution context for my {value}
            yield {
                "channel": channel,
                "reps": reps,
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
