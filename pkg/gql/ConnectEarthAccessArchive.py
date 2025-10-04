# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene
import journal
import qed

# my input types
from .GeoBBoxInput import GeoBBoxInput
from .GeoVertexInput import GeoVertexInput
from .GeoCircleInput import GeoCircleInput
from .GeoLineInput import GeoLineInput
from .GeoPolygonInput import GeoPolygonInput

# the result types
from .Archive import Archive


# add a new data archive to the pile
class ConnectEarthAccessArchive(graphene.Mutation):
    """
    Connect a new data archive
    """

    # inputs
    class Arguments:
        # the update context
        name = graphene.String(required=True)
        uri = graphene.String(required=True)
        filters = graphene.List(graphene.String)
        geo = graphene.String()
        bbox = GeoBBoxInput()
        point = GeoVertexInput()
        circle = GeoCircleInput()
        line = GeoLineInput()
        polygon = GeoPolygonInput()

    # the result is always an archive
    archive = graphene.Field(Archive)

    # the range controller mutator
    @staticmethod
    def mutate(
        root,
        info,
        name,
        uri,
        filters,
        geo,
        bbox,
        point,
        circle,
        line,
        polygon,
    ):
        """
        Add a new archive to the pile
        """
        # make a channel
        channel = journal.info("qed.archives.connect")
        # show me
        channel.line(f"{name=}")
        channel.indent()
        channel.line(f"{uri=}")
        channel.line(f"{filters=}")
        channel.line(f"{geo=}")
        channel.line(f"{point=}")
        channel.line(f"{circle=}")
        channel.line(f"{line=}")
        channel.line(f"{polygon=}")
        channel.outdent()
        # flush
        channel.log()

        # grab the store
        store = info.context["store"]
        # if the {uri} is already connected
        if store.archive(uri=uri):
            # make a channel
            channel = journal.warning("qed.gql.connect")
            # issue a warning
            channel.log(f"archive '{uri}' is already connected")
            # and bail
            return None
        # otherwise, parse the uri
        uri = qed.primitives.uri.parse(uri, scheme="file")
        # show me
        channel.log(f"connecting to archive {uri}")

        # unpack the filters;
        selectedFilters = []
        #  first the geographical searches
        if "geo" in filters:
            # build the name of the filter
            filterName = f"{name}.geo.{geo}"
            # if the selection is a bounding box
            if geo == "bbox":
                # make a geo bounding box
                filter = qed.archives.geoBBox(
                    name=filterName,
                    ne=(bbox["ne"]["longitude"], bbox["ne"]["latitude"]),
                    sw=(bbox["sw"]["longitude"], bbox["sw"]["latitude"]),
                )
            # if the selection is a point
            elif geo == "point":
                # make a geo point
                filter = qed.archives.geoPoint(name=filterName, **point)
            # if it's a circle
            elif geo == "circle":
                # make a geo circle
                filter = qed.archives.geoCircle(name=filterName, **circle)
            # if it's a line
            elif geo == "line":
                # parse the vertices
                vertices = qed.archives.geoLine.parseVertices(payload=line["vertices"])
                # and build the filter
                filter = qed.archives.geoLine(name=filterName, vertices=vertices)
            # if it's a polygon
            elif geo == "polygon":
                # parse the vertices
                vertices = qed.archives.geoPolygon.parseVertices(
                    payload=polygon["vertices"]
                )
                # and build the filter
                filter = qed.archives.geoPolygon(name=filterName, vertices=vertices)
            # otherwise
            else:
                # we have a bug
                bug = journal.firewall("qed.gql.connectArhive.earth")
                # report
                bug.line(f"unknown geo filter '{geo}'")
                bug.line(
                    f"while attempting to connect '{name}', an earth access archive"
                )
                bug.log()
                # and bail, just in case firewalls aren't fatal
                return
            # if all went well, add the filter to the pile
            filters.append(filter)

        # build a collection of datasets on earth access
        archive = qed.archives.earth(name=name, uri=uri, filters=filters)
        # add the new archive to the pile
        store.connectArchive(archive=archive)
        # report
        channel.line(f"connected to '{uri}', an earth access archive")
        channel.line("filters:")
        channel.indent()
        for filter in archive.filters:
            channel.line(f"{filter}")
        channel.outdent()
        channel.log()
        # make a resolution context
        context = {
            "archive": archive,
        }
        # and resolve the mutation
        return context


# end of file
