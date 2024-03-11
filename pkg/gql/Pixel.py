# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene


# a pixel
class Pixel(graphene.ObjectType):
    """
    A pixel
    """

    # the fields
    x = graphene.Int(required=True)
    y = graphene.Int(required=True)

    # the resolvers
    @staticmethod
    def resolve_x(pixel: tuple, *_):
        """
        Grab the x coordinate
        """
        # easy enough
        return pixel[1]

    @staticmethod
    def resolve_y(pixel: tuple, *_):
        """
        Grab the y coordinate
        """
        # easy enough
        return pixel[0]


# end of file
