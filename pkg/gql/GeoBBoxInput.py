# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene

# my parts
from .GeoVertexInput import GeoVertexInput


# the payload for the vertices of bounding box
class GeoBBoxInput(graphene.InputObjectType):
    """
    The payload for the vertices of a bounding box on earth
    """

    # the fields
    ne = GeoVertexInput()
    sw = GeoVertexInput()


# end of file
