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

    # the label the factory would have
    label = graphene.String(required=True)
    # the slots it would gain
    slots = graphene.List(graphene.NonNull(FlowPinPreviewSlot), required=True)
    # the ids of the slots it would let go of
    dropped = graphene.List(graphene.NonNull(graphene.ID), required=True)

    # resolvers
    @staticmethod
    def resolve_label(preview, info, **kwds):
        """
        Get the label the factory would have
        """
        # the preview knows
        return preview["label"]

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
