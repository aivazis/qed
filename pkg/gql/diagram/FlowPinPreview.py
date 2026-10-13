# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# field types
from .FlowPinPreviewSlot import FlowPinPreviewSlot


# what pinning a factory to a class would do
class FlowPinPreview(graphene.ObjectType):
    """
    What pinning a factory of a pipeline diagram to a class would do, worked out by the plan the
    pin itself carries out, without changing anything
    """

    # the parts of the label the factory would have: the family of the class, and the role of
    # the protocol it satisfies, if it is known
    family = graphene.String(required=True)
    role = graphene.String()
    # the slots it would gain
    slots = graphene.List(graphene.NonNull(FlowPinPreviewSlot), required=True)
    # the ids of the slots it would let go of
    dropped = graphene.List(graphene.NonNull(graphene.ID), required=True)

    # resolvers
    @staticmethod
    def resolve_family(preview, info, **kwds):
        """
        Get the family of the class the factory would be pinned to
        """
        # the preview knows
        return preview["family"]

    @staticmethod
    def resolve_role(preview, info, **kwds):
        """
        Get the role of the protocol the factory satisfies
        """
        # the preview knows
        return preview["role"]

    @staticmethod
    def resolve_slots(preview, info, **kwds):
        """
        Get the slots the factory would gain
        """
        # the preview knows
        return preview["fresh"]

    @staticmethod
    def resolve_dropped(preview, info, **kwds):
        """
        Get the ids of the slots the factory would let go of
        """
        # in the form the diagram uses for them
        return [slot.relay for slot in preview["left"]]


# end of file
