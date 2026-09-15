# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import graphene
import journal
import qed

# the request payload
from .ConnectEarthAccessArchiveInput import ConnectEarthAccessArchiveInput

# the result types
from .Archive import Archive


# add a new data archive to the pile
class ConnectEarthAccessArchive(graphene.Mutation):
    """
    Connect a new EarthAccess data archive
    """

    # inputs
    class Arguments:
        # the request payload
        input = ConnectEarthAccessArchiveInput(required=True)

    # the result is always an archive
    archive = graphene.Field(Archive)

    # the mutator
    @staticmethod
    def mutate(root, info, input):
        """
        Add a new archive to the pile
        """
        # unpack the payload
        name = input.name
        uri = input.uri
        # make a channel
        channel = journal.info("qed.archives.connect")
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
        # assemble the query out of the payload
        query = ConnectEarthAccessArchive.harvest(input=input)
        # a payload that does not form a query has already been reported
        if query is None:
            # so bail
            return None
        # build the archive
        archive = qed.archives.earth(name=name, uri=uri, **query)
        # add it to the pile
        store.connectArchive(archive=archive)
        # report
        channel.line(f"connected to '{uri}', an earth access archive")
        channel.line("query:")
        channel.indent()
        # with the query parameters
        for parameter, value in archive.query().items():
            # one per line
            channel.line(f"{parameter}: {value}")
        # outdent
        channel.outdent()
        # and flush
        channel.log()
        # make a resolution context
        context = {
            "archive": archive,
        }
        # and resolve the mutation
        return context

    # implementation details
    @staticmethod
    def harvest(input):
        """
        Extract the archive traits from the mutation {input}
        """
        # make a pile
        query = {}
        # the cap on the search results
        if input.count:
            # goes in as an integer
            query["count"] = int(input.count)
        # the collection
        collection = input.collection
        # if it is specified
        if collection is not None:
            # its short name
            if collection.shortName:
                # goes in
                query["collection"] = collection.shortName
            # and its concept id
            if collection.conceptId:
                # goes in
                query["conceptId"] = collection.conceptId
        # the granule name pattern
        granule = input.granule
        # if it is specified
        if granule is not None and granule.pattern:
            # goes in
            query["pattern"] = granule.pattern
        # the set of active filters
        filters = input.filters or []
        # the time window
        when = input.when
        # if it is active
        if "when" in filters and when is not None:
            # its ends go in, open where blank
            query["begin"] = when.begin or None
            query["end"] = when.end or None
        # the geographical restriction
        if "geo" in filters:
            # get its kind
            geo = input.geo
            # a bounding box
            if geo == "bbox":
                # get its corners
                sw = input.bbox.sw
                ne = input.bbox.ne
                # goes in as (west, south, east, north)
                query["bbox"] = (
                    float(sw.longitude),
                    float(sw.latitude),
                    float(ne.longitude),
                    float(ne.latitude),
                )
            # a point
            elif geo == "point":
                # get it
                point = input.point
                # goes in as (longitude, latitude)
                query["point"] = (float(point.longitude), float(point.latitude))
            # a circle
            elif geo == "circle":
                # get it
                circle = input.circle
                # goes in as (longitude, latitude, radius)
                query["circle"] = (
                    float(circle.longitude),
                    float(circle.latitude),
                    float(circle.radius),
                )
            # a line
            elif geo == "line":
                # its vertices go in
                query["line"] = ConnectEarthAccessArchive.vertices(payload=input.line.vertices)
            # a polygon
            elif geo == "polygon":
                # its vertices go in
                query["polygon"] = ConnectEarthAccessArchive.vertices(
                    payload=input.polygon.vertices
                )
            # anything else
            else:
                # is a bug
                bug = journal.firewall("qed.gql.connectArchive.earth")
                # report
                bug.line(f"unknown geo filter '{geo}'")
                bug.line(f"while attempting to connect '{input.name}', an earth access archive")
                bug.log()
                # and bail, just in case firewalls aren't fatal
                return None
        # all done
        return query

    @staticmethod
    def vertices(payload):
        """
        Convert {payload}, a list of vertices, into (longitude, latitude) pairs
        """
        # one pair per vertex
        return [(float(vertex.longitude), float(vertex.latitude)) for vertex in payload]


# end of file
