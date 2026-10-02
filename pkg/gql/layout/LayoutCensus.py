# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# my parts
from .LayoutMeasure import LayoutMeasure


# the census a raster is compared against
class LayoutCensus(graphene.ObjectType):
    """
    The census of the kind of product a raster belongs to, and where the raster falls in it
    """

    # the name of the census
    census = graphene.String(required=True)
    # the product and the cycle it covers
    product = graphene.String()
    cycle = graphene.Int()
    # the kind of raster the comparison is against, or {None} for all the rasters of the census
    kind = graphene.String()
    # how many rasters it compares against, and how many granules it measured
    rasters = graphene.Int(required=True)
    granules = graphene.Int(required=True)
    # the measures
    measures = graphene.List(graphene.NonNull(LayoutMeasure), required=True)


# end of file
