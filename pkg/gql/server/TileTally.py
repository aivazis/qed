# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the recent tiles that were served one way
class TileTally(graphene.ObjectType):
    """
    The recent tiles that were served one way, and how long they took
    """

    # how they were served: crew, hit, inline, refused, starved, or hangup
    via = graphene.String(required=True)
    # how many of them
    count = graphene.Int(required=True)
    # their median and 95th percentile wall times, in seconds
    median = graphene.Float(required=True)
    p95 = graphene.Float(required=True)


# end of file
