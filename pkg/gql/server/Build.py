# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# my parts
from .RasterBuild import RasterBuild


# the preparation of a dataset
class Build(graphene.ObjectType):
    """
    The work that makes a dataset worth looking at: the pyramids of the dataset and of the
    rasters it is read with, with its status, its times, and how deep its levels are available
    """

    # the dataset
    dataset = graphene.String(required=True)
    # its status: working, seeded, ready, or failed
    status = graphene.String(required=True)
    # the reason of a failure
    error = graphene.String()
    # when the work started, when the view became worth looking at, and when the work finished,
    # in seconds since the epoch
    started = graphene.Float(required=True)
    seeded = graphene.Float()
    finished = graphene.Float()
    # the deepest level of the pyramid, and the deepest level available for every raster
    depth = graphene.Int(required=True)
    reach = graphene.Int(required=True)
    # the build of each raster
    rasters = graphene.List(graphene.NonNull(RasterBuild), required=True)


# end of file
