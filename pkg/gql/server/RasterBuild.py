# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the pyramid of one raster under construction
class RasterBuild(graphene.ObjectType):
    """
    The pyramid of one raster: how deep it goes, how deep it is available, and the level under
    construction
    """

    # the raster
    raster = graphene.String(required=True)
    # the deepest level the build makes
    depth = graphene.Int(required=True)
    # the deepest level available, counting from the first without gaps
    reach = graphene.Int(required=True)
    # the level under construction, while there is one
    level = graphene.Int()
    # the runs of that level, and the ones still out
    runs = graphene.Int(required=True)
    outstanding = graphene.Int(required=True)
    # the pages its runs fetched from the product, as far as the file can tell
    fetched = graphene.Int(required=True)


# end of file
