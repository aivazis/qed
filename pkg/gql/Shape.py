# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene


# the server version
class Shape(graphene.ObjectType):
    """
    The shape of a raster
    """

    # the fields
    lines = graphene.String(required=True)
    samples = graphene.String(required=True)


# end of file
