# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene


# the payload for a point on earth
class GeoVertexInput(graphene.InputObjectType):
    """
    The payload for a point on earth
    """

    # the fields
    longitude = graphene.String(required=True)
    latitude = graphene.String(required=True)


# end of file
