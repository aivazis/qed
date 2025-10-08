# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed
import journal

# superclass
from .Filter import Filter


# a point on the surface of a sphere
class Circle(Filter, family="qed.archives.filters.circle"):
    """
    A filter for earthdata searches that identifies datasets that contain a specific point
    """

    # user-configurable state
    radius = qed.properties.float()
    radius.doc = "the radius of the circle, in meters"

    longitude = qed.properties.float()
    longitude.doc = "the longitude of the center"

    latitude = qed.properties.float()
    latitude.doc = "the latitude of the center"

    # implementation details
    # visitor support
    def onEarthAccess(self, **kwds):
        """
        Generate the required representation so an {EarthAccess} archive can filter its contents
        """
        # produce the {earthaccess} keyword
        yield (
            # the name
            "circle",
            # the contents
            (self.longitude, self.latitude, self.radius),
        )
        # all done
        return


# end of file
