# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene


# the query of an earth access archive
class EarthAccessQuery(graphene.ObjectType):
    """
    The traits of an earth access archive that make up its query, as the archive holds them
    """

    # the short name of the collection
    collection = graphene.String()
    # its concept id
    conceptId = graphene.String()
    # the pattern the granule names must match
    pattern = graphene.String()
    # the cap on the number of granules fetched
    count = graphene.Int()
    # the start of the acquisition window
    begin = graphene.String()
    # its end
    end = graphene.String()
    # a bounding box, as (west, south, east, north)
    bbox = graphene.List(graphene.Float)
    # a point, as (longitude, latitude)
    point = graphene.List(graphene.Float)
    # a circle, as (longitude, latitude, radius)
    circle = graphene.List(graphene.Float)
    # the (longitude, latitude) vertices of a line
    line = graphene.List(graphene.List(graphene.Float))
    # the (longitude, latitude) vertices of a polygon
    polygon = graphene.List(graphene.List(graphene.Float))


# end of file
