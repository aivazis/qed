# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene
# the channel value projections
from .ChannelValue import ChannelValue


# a pixel value as represented by a channel
class ChannelRep(graphene.ObjectType):
    """
    The value of a dataset sample
    """

    # fields
    channel = graphene.String()
    reps = graphene.List(ChannelValue)


    # resolvers
    def resolve_reps(context, info, **kwds):
        """
        Unpack the channel value representations
        """
        reps = context["reps"]
        # go through them
        for rep, units in reps:
            # build context for the channel value resolvers
            yield {
                "rep": rep,
                "units": units,
            }

        # all done
        return


# end of file
