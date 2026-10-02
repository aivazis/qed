# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# how the chunks of a raster sit on the pages of its file
class LayoutSummary(graphene.ObjectType):
    """
    How the chunks of a raster sit on the pages of its file; the page measures are missing for
    a file that is not paged
    """

    # the chunks the tiling describes, and the ones that were written
    grid = graphene.Int(required=True)
    written = graphene.Int(required=True)
    # the bytes they store, and the size of a chunk before compression
    stored = graphene.Float(required=True)
    raw = graphene.Float(required=True)
    compression = graphene.Float()
    # the nearly empty chunks, and the bytes they store
    empty = graphene.Int(required=True)
    emptyStored = graphene.Float(required=True)
    # the pages the raster touches, and the ones that hold nothing but its nearly empty chunks
    pages = graphene.Int()
    emptyPages = graphene.Int()
    # the bytes moved per byte stored: reading the chunks one at a time, reading them all with
    # each page fetched once, and reading them with the datasets that share their pages
    alone = graphene.Float()
    once = graphene.Float()
    joint = graphene.Float()
    # the share of each page the raster fills, and the share all the datasets fill
    fillMedian = graphene.Float()
    fillMean = graphene.Float()
    fillFull = graphene.Float()
    totalMean = graphene.Float()
    # the chunks of any dataset per page
    tenants = graphene.Float()
    # the share of consecutive chunks on a page that are neighbors on the raster
    locality = graphene.Float()
    # the histograms, as counts of equal bins between zero and one: the stored size of a chunk
    # as a share of its raw size, the share of a page the raster fills, and the share all the
    # datasets fill
    sizes = graphene.List(graphene.NonNull(graphene.Int), required=True)
    fill = graphene.List(graphene.NonNull(graphene.Int))
    total = graphene.List(graphene.NonNull(graphene.Int))


# end of file
