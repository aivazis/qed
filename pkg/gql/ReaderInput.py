# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene


# the payload for an update to the range of a controller
class ReaderInput(graphene.InputObjectType):
    """
    The payload for a new reader connection
    """

    # the fields
    reader = graphene.String(required=True)
    name = graphene.String(required=True)
    uri = graphene.String(required=True)
    lines = graphene.String(required=False)
    samples = graphene.String(required=False)
    cell = graphene.String(required=False)


# end of file
