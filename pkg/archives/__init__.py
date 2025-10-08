# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# publish
from .Local import Local as local
from .S3 import S3 as s3

# earth access and its filters
from .EarthAccess import EarthAccess as earth

from .BBox import BBox as bbox
from .Circle import Circle as circle
from .Collection import Collection as collection
from .Count import Count as count
from .Granule import Granule as granule
from .Line import Line as line
from .Polygon import Polygon as polygon
from .Point import Point as point
from .Window import Window as window


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
