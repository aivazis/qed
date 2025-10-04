# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# publish
from .Local import Local as local
from .S3 import S3 as s3

# earth access and its filters
from .EarthAccess import EarthAccess as earth
from .GeoBBox import GeoBBox as geoBBox
from .GeoPoint import GeoPoint as geoPoint
from .GeoCircle import GeoCircle as geoCircle
from .GeoLine import GeoLine as geoLine
from .GeoPolygon import GeoPolygon as geoPolygon


# discovery
def supported():
    """
    Return a list of known archive types
    """
    # build this by hand, for now
    return (local, s3, earth)


def available():
    """
    Generate a sequence of the archive type for which there is available runtime support
    """
    # go through the available types
    for factory in supported():
        # ask the archive to determine whether there is runtime support
        if factory.isSupported():
            # and if so, make it available
            yield factory
    # all done
    return


# end of file
