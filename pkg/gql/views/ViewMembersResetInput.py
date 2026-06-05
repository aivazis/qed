# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for restoring a stack's default participation mask
class ViewMembersResetInput(graphene.InputObjectType):
    """
    The payload for restoring a stack's default participation mask
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the stack to act on
    reader = graphene.String(required=True)


# end of file
