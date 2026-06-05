# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for setting a stack's participation mask
class ViewMembersSetInput(graphene.InputObjectType):
    """
    The payload for setting which members of a stack participate in its aggregate
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the stack to act on
    reader = graphene.String(required=True)
    # the per-member participation mask, aligned to the stack's member order
    members = graphene.List(graphene.NonNull(graphene.Boolean), required=True)


# end of file
