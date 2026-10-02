# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# my parts
from .LayoutFileMapRaster import LayoutFileMapRaster


# what every page of a file holds
class LayoutFileMap(graphene.ObjectType):
    """
    What every page of a paged file holds, in file order, as lists with one entry per page: the
    bytes and chunks of each raster of the product, and the bytes of the datasets the product does
    not display; the rest of a page is metadata or free
    """

    # the number of pages
    pages = graphene.Int(required=True)
    # the rasters of the product
    rasters = graphene.List(graphene.NonNull(LayoutFileMapRaster), required=True)
    # the position of the raster in view among them
    selected = graphene.Int()
    # the bytes of the datasets the product does not display
    others = graphene.List(graphene.NonNull(graphene.Int), required=True)


# end of file
