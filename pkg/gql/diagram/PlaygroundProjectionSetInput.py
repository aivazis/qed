# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the payload of a change to the projection of the playground
class PlaygroundProjectionSetInput(graphene.InputObjectType):
    """
    The payload to change how the diagram of the playground is projected
    """

    # flat or isometric
    kind = graphene.String(required=True)
    # the quarter turns of an isometric view
    azimuth = graphene.Int(required=True)
    # whether an isometric view looks from below the floor
    below = graphene.Boolean(required=True)


# end of file
