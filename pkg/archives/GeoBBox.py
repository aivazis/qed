# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed
import journal

# superclass
from .Filter import Filter


# a polygon on the surface of a sphere
class GeoBBox(Filter, family="qed.archives.filters.geoBBox"):
    """
    A filter for earthdata searches that identifies datasets that contain a specific point
    """

    # user-configurable state
    ne = qed.properties.tuple(schema=qed.properties.float())
    ne.doc = "the coordinates of the north east corner"

    sw = qed.properties.tuple(schema=qed.properties.float())
    sw.doc = "the coordinates of the south west corner"

    # implementation details
    # visitor support
    def onEarthAccess(self, **kwds):
        """
        Generate the required representation so an {EarthAccess} archive can filter its contents
        """
        # unpack my state
        swLon, swLat = self.sw
        neLon, neLat = self.ne
        # produce the {earthaccess} keyword
        yield (
            # the name
            "bounding_box",
            # the contents
            (swLon, swLat, neLon, neLat),
        )
        # all done
        return


# end of file
