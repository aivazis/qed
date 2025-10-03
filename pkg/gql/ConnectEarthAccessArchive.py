# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# externals
import graphene
import journal
import qed

# my input types
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
        # build a collection of datasets on earth access
        archive = qed.archives.earth(name=name, uri=uri)
        # add the new archive to the pile
        store.connectArchive(archive=archive)
        # report
        channel.log(f"connected to '{uri}'")
        # make a resolution context
        context = {
            "archive": archive,
        }
        # and resolve the mutation
        return context


# end of file
