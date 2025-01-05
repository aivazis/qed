# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene


# a pixel value as represented by a channel
class ChannelValue(graphene.ObjectType):
    """
    The value of a dataset sample expressed in specific units
    """

    # fields
    rep = graphene.String()
    units = graphene.String()

    # resolvers
    @staticmethod
    def resolve_rep(context, info, **kwds):
        """
        Generate the representation of the value
        """
        # extract the value
        value = context["rep"]
        # if it's a string
        if isinstance(value, str):
            # leave it alone
            return value
        # otherwise, render it and return it
        return f"{value:10.4g}"


# end of file
