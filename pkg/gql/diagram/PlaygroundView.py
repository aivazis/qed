# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# where the cameras look
from .PlaygroundCamera import PlaygroundCamera


# how the playground is looked at
class PlaygroundView(graphene.ObjectType):
    """
    How every client looks at the playground: the projection of its diagram, the trays of its
    panel that are open, and where the cameras look
    """

    # the fields
    # there is only one, so its id is fixed; it lets a mutation's answer update the clients' cache
    id = graphene.ID(required=True)
    # flat or isometric
    kind = graphene.String(required=True)
    # the quarter turns of an isometric view, in [0, 4)
    azimuth = graphene.Int(required=True)
    # whether an isometric view looks from below the floor
    below = graphene.Boolean(required=True)
    # the names of the trays that are open
    trays = graphene.List(graphene.NonNull(graphene.String), required=True)
    # where every client's camera looks, once some client has moved its camera
    camera = graphene.Field(PlaygroundCamera)

    # resolvers
    @staticmethod
    def resolve_id(view, info, **kwds):
        """
        Make an id
        """
        # there is only one
        return "playground.view"


# end of file
