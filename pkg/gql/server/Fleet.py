# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# my parts
from .Team import Team


# the teams of worker processes
class Fleet(graphene.ObjectType):
    """
    The teams of worker processes the server has formed
    """

    # the teams
    teams = graphene.List(graphene.NonNull(Team), required=True)


# end of file
