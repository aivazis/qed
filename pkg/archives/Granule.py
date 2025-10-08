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
class Granule(Filter, family="qed.archives.filters.granule"):
    """
    A filter for earthdata searches that identifies a pattern to match against the granule name
    """

    # user-configurable state
    pattern = qed.properties.str()
    pattern.doc = "a pattern to match against the granule name"

    # implementation details
    # visitor support
    def onEarthAccess(self, **kwds):
        """
        Generate the required representation so an {EarthAccess} archive can filter its contents
        """
        # unpack my state
        pattern = self.pattern
        # if the pattern is non-trivial
        if pattern:
            # produce the {earthaccess} keyword
            yield (
                # the pattern
                "granule_name",
                # the contents
                pattern,
            )

        # all done
        return


# end of file
