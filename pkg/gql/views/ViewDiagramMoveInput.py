# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for moving a node of the pipeline diagram
class ViewDiagramMoveInput(graphene.InputObjectType):
    """
    The payload to move a node of the pipeline diagram of a viewport
    """

    # the viewport
    viewport = graphene.Int(required=True)
    # the id of the node
    node = graphene.ID(required=True)
    # where it goes
    x = graphene.Float(required=True)
    y = graphene.Float(required=True)
    z = graphene.Float(required=True)
    # whether this is where the node lands, or a step of a drag still in progress
    settled = graphene.Boolean(default_value=True)


# end of file
