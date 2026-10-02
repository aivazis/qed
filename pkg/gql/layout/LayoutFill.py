# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# what a raster holds where there is no data
class LayoutFill(graphene.ObjectType):
    """
    The fill of a raster: the value the library knows about, the value the conventions of the
    format declare, what the smallest chunk actually holds, the chunks that hold nothing else,
    and what they cost
    """

    # the fill value status of the raster, as the library reports it
    status = graphene.String()
    # the fill value the library hands out for the chunks that were never written
    hdf5 = graphene.String()
    # the value of the {_FillValue} attribute
    cf = graphene.String()
    # what the smallest chunk holds: a value, "data", or "unknown"
    holds = graphene.String()
    # whether the library's fill is what the chunks of fill hold
    agrees = graphene.Boolean()
    # the chunks that hold nothing but the fill, and the bytes they store
    chunks = graphene.Int()
    bytes = graphene.Float()
    # the deflate level that reproduces them
    level = graphene.Int()
    # the times, in ms: decoding a chunk of fill, making it from its value, encoding it, and
    # decoding a typical chunk of data
    decodeMs = graphene.Float()
    makeMs = graphene.Float()
    encodeMs = graphene.Float()
    dataDecodeMs = graphene.Float()


# end of file
