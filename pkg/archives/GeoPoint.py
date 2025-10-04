# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed
import journal


# a point on the surface of a sphere
class GeoPoint(
    qed.component,
    family="qed.archives.filters.geoPoint",
    implements=qed.protocols.archiveFilter,
):
    """
    A filter for earthdata searches that identifies datasets that contain a specific point
    """

    # user-configurable state
    longitude = qed.properties.float()
    longitude.doc = "the longitude of the point"

    latitude = qed.properties.float()
    latitude.doc = "the latitude of the point"

    # interface
    @qed.export
    def filter(self):
        """
        Apply the filter to a search
        """
        # all done
        return


# end of file
