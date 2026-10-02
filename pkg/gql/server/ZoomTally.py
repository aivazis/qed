# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the tile requests at one zoom
class ZoomTally(graphene.ObjectType):
    """
    How many tile requests arrived at one zoom
    """

    # the zoom, along each axis
    vertical = graphene.Int(required=True)
    horizontal = graphene.Int(required=True)
    # the number of requests
    count = graphene.Int(required=True)


# end of file
