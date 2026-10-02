# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# a raster on the map of its file
class LayoutFileMapRaster(graphene.ObjectType):
    """
    A raster of the product on the map of its file: its name, and its bytes and the number of its
    chunks on each page of the file
    """

    # the name of the raster within its product
    name = graphene.String(required=True)
    # its bytes on each page
    bytes = graphene.List(graphene.NonNull(graphene.Int), required=True)
    # the number of its chunks on each page
    chunks = graphene.List(graphene.NonNull(graphene.Int), required=True)


# end of file
