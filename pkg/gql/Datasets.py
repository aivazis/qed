# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# externals
import graphene


# the server version
class Datasets(graphene.ObjectType):
    """
    The collection of known data sets
    """

    # the fields
    id = graphene.ID()


# end of file
