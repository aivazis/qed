# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for toggling a sync aspect across all viewports
class ViewSyncToggleAllInput(graphene.InputObjectType):
    """
    The payload to toggle a sync aspect across all viewports
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the sync aspect to toggle
    aspect = graphene.String(required=True)


# end of file
