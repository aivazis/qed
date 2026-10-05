# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for moving a group of nodes of the pipeline diagram
class DiagramMoveGroupInput(graphene.InputObjectType):
    """
    The payload to move a group of nodes of a pipeline diagram
    """

    # the id of the diagram
    diagram = graphene.ID(required=True)
    # the ids of the nodes
    nodes = graphene.List(graphene.NonNull(graphene.ID), required=True)
    # the id of the node that leads the group
    anchor = graphene.ID(required=True)
    # where the lead goes; the rest keep their places around it
    x = graphene.Float(required=True)
    y = graphene.Float(required=True)
    z = graphene.Float(required=True)


# end of file
