# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the chunk grid of a raster
class LayoutGrid(graphene.ObjectType):
    """
    The cells of the chunk grid of a raster, in row major order: the state of each, as its
    index in {states}, and the stored size of its chunk, zero for the cells never written
    """

    # the extent of the grid
    rows = graphene.Int(required=True)
    cols = graphene.Int(required=True)
    # the names of the states, in the order of their codes
    states = graphene.List(graphene.NonNull(graphene.String), required=True)
    # the state of each cell
    codes = graphene.List(graphene.NonNull(graphene.Int), required=True)
    # and the stored size of its chunk
    sizes = graphene.List(graphene.NonNull(graphene.Int), required=True)


# end of file
