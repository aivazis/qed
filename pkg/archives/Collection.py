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
class Collection(Filter, family="qed.archives.filters.collection"):
    """
    A filter for earthdata searches that identifies the data collection that matching datasets
    should belong to
    """

    # user-configurable state
    shortName = qed.properties.str()
    shortName.doc = "the short name of the collection"

    conceptId = qed.properties.str()
    conceptId.doc = "the concept id of the collection"

    # implementation details
    # visitor support
    def onEarthAccess(self, **kwds):
        """
        Generate the required representation so an {EarthAccess} archive can filter its contents
        """
        # unpack my state
        shortName = self.shortName
        conceptId = self.conceptId
        # if the name is non-trivial
        if shortName:
            # produce the {earthaccess} keyword
            yield (
                # the name
                "short_name",
                # the contents
                shortName,
            )
        # if the concept id is non-trivial
        if conceptId:
            # produce the {earthaccess} keyword
            yield (
                # the name
                "concept_id",
                # the contents
                conceptId,
            )

        # all done
        return


# end of file
