# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the request payload for staging data sources
class StageInput(graphene.InputObjectType):
    """
    The payload to stage connected data sources
    """

    # the source to stage; a trivial value stages every connected source
    reader = graphene.String(required=False)


# end of file
