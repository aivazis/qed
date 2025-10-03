# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene


# the payload for a circle centered at some point on earth
class GeoCircleInput(graphene.InputObjectType):
    """
    The payload for a circle centered at some point on earth
    """

    # the fields
    radius = graphene.String(required=True)
    longitude = graphene.String(required=True)
    latitude = graphene.String(required=True)


# end of file
