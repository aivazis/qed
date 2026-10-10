# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for picking the engine that draws the tiles of a view
class ViewEngineSetInput(graphene.InputObjectType):
    """
    The payload for picking the engine that draws the tiles of a view
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the engine: flow, or iterators
    engine = graphene.String(required=True)


# end of file
