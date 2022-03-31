# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import graphene


# a pixel value as represented by a channel
class ChannelRep(graphene.ObjectType):
    """
    The value of a dataset sample
    """

    # fields
    channel = graphene.String()
    rep = graphene.String()


# end of file
