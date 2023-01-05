# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


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
    def resolve_rep(context, info, **kwds):
        """
        Generate the representation of the value
        """
        # extract the value
        rep = context["rep"]
        # fixed point
        return f"{rep:.3f}"


# end of file
