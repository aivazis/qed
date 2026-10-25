# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the payload of a move of the cameras on the playground
class PlaygroundCameraSetInput(graphene.InputObjectType):
    """
    The payload to point every client's camera at a place on the playground
    """

    # the diagram point at the middle of the view
    x = graphene.Float(required=True)
    # in both of its coordinates
    y = graphene.Float(required=True)
    # the zoom: the distance of the camera from the diagram
    z = graphene.Float(required=True)


# end of file
