# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for updating the sync scroll offset
class ViewSyncUpdateOffsetInput(graphene.InputObjectType):
    """
    The payload to update the sync scroll offset
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the horizontal offset
    x = graphene.Int(required=True)
    # the vertical offset
    y = graphene.Int(required=True)


# end of file
