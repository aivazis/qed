# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the payload of opening or closing a tray of the playground
class PlaygroundTraySetInput(graphene.InputObjectType):
    """
    The payload to open or close a tray of the playground's panel
    """

    # the name of the tray
    tray = graphene.String(required=True)
    # whether it is open
    expanded = graphene.Boolean(required=True)


# end of file
