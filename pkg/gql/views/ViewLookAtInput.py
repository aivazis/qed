# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for setting the look-at center
class ViewLookAtInput(graphene.InputObjectType):
    """
    The payload to set the look-at center
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the source row under the viewport center
    row = graphene.Float(required=True)
    # the source column under the viewport center
    col = graphene.Float(required=True)


# end of file
