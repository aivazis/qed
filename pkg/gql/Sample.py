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
        # all done
        return [0,0]


    def resolve_pixel(context, info, **kwds):
        """
        Get the value of a dataset at the specified location
        """
        # all done
        return [context["line"], context["sample"]]


# end of file
