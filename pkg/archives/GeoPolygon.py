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
class GeoPolygon(Filter, family="qed.archives.filters.geoPolygon"):
    """
    A filter for earthdata searches that identifies datasets that contain a specific point
    """

    # user-configurable state
    vertices = qed.properties.list(
        schema=qed.properties.tuple(schema=qed.properties.float())
    )
    vertices.doc = "the collection of (lon, lat) vertices that make up the polygon"

    # implementation details
    # visitor support
    def onEarthAccess(self, **kwds):
        """
        Generate the required representation so an {EarthAccess} archive can filter its contents
        """
        # get my vertices
        vertices = self.vertices
        # if there is only one
        if len(vertices) == 1:
            # pretend i'm a point
            yield (
                # the name
                "point",
                # the payload
                vertices[0],
            )
            # all done
            return
        # if there are two
        if len(vertices) == 2:
            # pretend i'm a line
            yield (
                # the name
                "line",
                # the payload
                vertices,
            )
        # if the user didn't bother to close the poylgon
        if vertices[0] != vertices[-1]:
            # make a copy
            vertices = list(vertices)
            # and close it by repeating the first vertex
            vertices.append(vertices[0])
        # produce the {earthaccess} keyword
        yield (
            # the name
            "polygon",
            # the contents
            vertices,
        )
        # all done
        return

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
