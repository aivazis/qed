# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the pages a raster lands on
class LayoutStrip(graphene.ObjectType):
    """
    The pages the chunks of a raster land on, in file order, as parallel lists with one entry per
    page: its number, the bytes of the raster on it and the number of its chunks, the bytes of all
    the other datasets together, and the other dataset with the most bytes on it
    """

    # the page numbers
    pages = graphene.List(graphene.NonNull(graphene.Int), required=True)
    # the bytes of the raster on each page, and the number of its chunks there
    mine = graphene.List(graphene.NonNull(graphene.Int), required=True)
    chunks = graphene.List(graphene.NonNull(graphene.Int), required=True)
    # the bytes of every other dataset together
    others = graphene.List(graphene.NonNull(graphene.Int), required=True)
    # the other dataset with the most bytes on each page, blank when there is none, and its bytes
    partner = graphene.List(graphene.NonNull(graphene.String), required=True)
    partnerBytes = graphene.List(graphene.NonNull(graphene.Int), required=True)


# end of file
