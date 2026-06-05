# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene

# the nested payloads
from .DataCollectionInput import DataCollectionInput
from .DataGranuleInput import DataGranuleInput
from .TimeIntervalInput import TimeIntervalInput
from .GeoBBoxInput import GeoBBoxInput
from .GeoVertexInput import GeoVertexInput
from .GeoCircleInput import GeoCircleInput
from .GeoLineInput import GeoLineInput
from .GeoPolygonInput import GeoPolygonInput


# the request payload for connecting an EarthAccess data archive
class ConnectEarthAccessArchiveInput(graphene.InputObjectType):
    """
    The payload to connect a new EarthAccess data archive
    """

    # the archive name
    name = graphene.String(required=True)
    # the archive uri
    uri = graphene.String(required=True)
    # an optional limit on the number of results
    count = graphene.String()
    # the data granule restriction
    granule = DataGranuleInput()
    # the data collection restriction
    collection = DataCollectionInput()
    # the set of active filters
    filters = graphene.List(graphene.String)
    # the time interval restriction
    when = TimeIntervalInput()
    # the kind of geographical restriction
    geo = graphene.String()
    # the geographical restriction payloads
    bbox = GeoBBoxInput()
    point = GeoVertexInput()
    circle = GeoCircleInput()
    line = GeoLineInput()
    polygon = GeoPolygonInput()


# end of file
