# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed
import journal


# a polygon on the surface of a sphere
class GeoBBox(
    qed.component,
    family="qed.archives.filters.geoBBox",
    implements=qed.protocols.archiveFilter,
):
    """
    A filter for earthdata searches that identifies datasets that contain a specific point
    """

    # user-configurable state
    ne = qed.properties.tuple(schema=qed.properties.float())
    ne.doc = "the coordinates of the north east corner"

    sw = qed.properties.tuple(schema=qed.properties.float())
    sw.doc = "the coordinates of the south west corner"

    # interface
    @qed.export
    def filter(self):
        """
        Apply the filter to a search
        """
        # all done
        return


# end of file
