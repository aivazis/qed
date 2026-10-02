# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# my parts
from .TileTally import TileTally
from .ZoomTally import ZoomTally


# the tile requests of the server
class ServerRequests(graphene.ObjectType):
    """
    The tile requests of the server: the ones waiting, the zooms they arrived at, and how the
    recent ones were served
    """

    # the requests waiting for a worker, and how long the oldest has waited, in seconds
    waiting = graphene.Int(required=True)
    oldest = graphene.Float(required=True)
    # the requests at each zoom, since the server started
    zooms = graphene.List(graphene.NonNull(ZoomTally), required=True)
    # how the recent tiles were served
    tiles = graphene.List(graphene.NonNull(TileTally), required=True)


# end of file
