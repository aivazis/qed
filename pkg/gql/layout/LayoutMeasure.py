# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# a measure of a raster, against the census of its kind
class LayoutMeasure(graphene.ObjectType):
    """
    A measure of a raster, and how it is distributed over the rasters of the census of its kind
    of product
    """

    # the name of the measure, and what it measures
    name = graphene.String(required=True)
    label = graphene.String(required=True)
    # whether a lower value is better, or {None} when neither is
    lower = graphene.Boolean()
    # the value of this raster, if it has one
    value = graphene.Float()
    # the number of rasters of the census that have one
    count = graphene.Int(required=True)
    # the percentiles
    p10 = graphene.Float(required=True)
    median = graphene.Float(required=True)
    p90 = graphene.Float(required=True)
    max = graphene.Float(required=True)
    # the range of the histogram, and its counts in bins of equal width
    low = graphene.Float(required=True)
    high = graphene.Float(required=True)
    bins = graphene.List(graphene.NonNull(graphene.Int), required=True)


# end of file
