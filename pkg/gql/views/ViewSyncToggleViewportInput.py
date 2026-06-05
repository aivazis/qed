# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for toggling a sync aspect for a single viewport
class ViewSyncToggleViewportInput(graphene.InputObjectType):
    """
    The payload to toggle a sync aspect for a single viewport
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the sync aspect to toggle
    aspect = graphene.String(required=True)


# end of file
