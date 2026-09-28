# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the cache of rendered tiles
class TileCache(graphene.ObjectType):
    """
    The cache of rendered tiles: its budgets, what it holds, and how it is doing
    """

    # the most bytes it may hold, and the most entries
    capacity = graphene.Float(required=True)
    slots = graphene.Int(required=True)
    # what it holds
    entries = graphene.Int(required=True)
    bytes = graphene.Float(required=True)
    # the requests it answered, and the ones it could not
    hits = graphene.Int(required=True)
    misses = graphene.Int(required=True)


# end of file
