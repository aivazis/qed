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
class Window(Filter, family="qed.archives.filters.window"):
    """
    A filter for earthdata searches that identifies datasets from a given time interval
    """

    # user-configurable state
    begin = qed.properties.str()
    begin.doc = "the longitude of the point"

    end = qed.properties.str()
    end.doc = "the latitude of the point"

    # implementation details
    # visitor support
    def onEarthAccess(self, **kwds):
        """
        Generate the required representation so an {EarthAccess} archive can filter its contents
        """
        # produce the {earthaccess} keyword
        yield (
            # the name
            "temporal",
            # the contents
            (self.begin, self.end),
        )
        # all done
        return


# end of file
