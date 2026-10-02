# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# a dataset that shares the pages of a raster
class LayoutPartner(graphene.ObjectType):
    """
    A dataset that shares the pages of a raster, and the bytes it has on them
    """

    # the name of the dataset, or its path in the file when its reader does not display it
    name = graphene.String(required=True)
    # the bytes it has on the pages of the raster
    bytes = graphene.Float(required=True)


# end of file
