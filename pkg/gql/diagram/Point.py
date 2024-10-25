# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import graphene


# the position of a node in client native coordinates
class Point(graphene.ObjectType):
    """
    A point in the intrinsic diagram coordinate system
    """

    # the fields
    x = graphene.Float(required=True)
    y = graphene.Float(required=True)


# end of file
