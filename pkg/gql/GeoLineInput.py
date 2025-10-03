# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene

# my parts
from .GeoVertexInput import GeoVertexInput


# the payload for a collection of line segments on earth
class GeoLineInput(graphene.InputObjectType):
    """
    The payload for a collection of line segments on earth
    """

    # the fields
    vertices = graphene.List(GeoVertexInput)


# end of file
