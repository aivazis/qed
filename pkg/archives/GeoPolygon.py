# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed
import journal


# a polygon on the surface of a sphere
class GeoPolygon(
    qed.component,
    family="qed.archives.filters.geoPolygon",
    implements=qed.protocols.archiveFilter,
):
    """
    A filter for earthdata searches that identifies datasets that contain a specific point
    """

    # user-configurable state
    vertices = qed.properties.list(
        schema=qed.properties.tuple(schema=qed.properties.float())
    )
    vertices.doc = "the collection of (lon, lat) vertices that make up the polygon"

    # interface
    @qed.export
    def filter(self):
        """
        Apply the filter to a search
        """
        # all done
        return

    # implementation details
    @classmethod
    def parseVertices(cls, payload):
        """
        Apply the schema of my {vertices} to {payload}, a list of dicts
        """
        # go through the payload
        for vertex in payload:
            # get the longitude
            lon = float(vertex["longitude"])
            # and the latitude
            lat = float(vertex["latitude"])
            # pack and ship
            yield (lon, lat)
        # all done
        return


# end of file
