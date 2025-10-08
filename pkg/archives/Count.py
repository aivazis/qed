# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed
import journal

# superclass
from .Filter import Filter


# limit the search results
class Count(Filter, family="qed.archives.filters.count"):
    """
    A filter for earthdata searches that limits the size of results
    """

    # user-configurable state
    count = qed.properties.int()
    count.doc = "limit the search results"

    # implementation details
    # visitor support
    def onEarthAccess(self, **kwds):
        """
        Generate the required representation so an {EarthAccess} archive can filter its contents
        """
        # produce the {earthaccess} keyword
        yield (
            # the name
            "count",
            # the contents
            self.count,
        )
        # all done
        return


# end of file
