# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene


# a sample from a dataset
class Sample(graphene.ObjectType):
    """
    The value of a dataset sample
    """

    # fields
    pixel = graphene.List(graphene.Int)
    value = graphene.List(graphene.Float)


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

        # extract the data payload and return it
        return profile[0][2:]


    def resolve_pixel(context, info, **kwds):
        """
        Get the value of a dataset at the specified location
        """
        # all done
        return [context["line"], context["sample"]]


# end of file
