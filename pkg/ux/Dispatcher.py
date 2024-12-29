# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# externals
import csv
import functools
import io
import re
import signal
import urllib
import uuid

# support
import journal
import qed

# the query handler
from .GraphQL import GraphQL


# the main request dispatcher
class Dispatcher:
    """
    The handler of web requests
    """

    # interface
    def dispatch(self, plexus, server, request):
        """
        Analyze the {request} received by the {server} and invoke the appropriate {plexus} behavior
        """
        # get the request type
        command = request.command
        # get the request uri
        url = request.url

        # make a channel
        channel = journal.debug("qed.ux.dispatch.url")
        # and show me the {url}
        channel.log(f"{command}: {url}")

        # take a look
        match = self.regex.match(url)
        # if there is no match
        if not match:
            # we have a bug
            channel = journal.firewall("qed.ux.dispatch")
            # complain
            channel.line(f"could not find handler")
            channel.line(f"while resolving ${url}")
            # flush
            channel.log()
            # and return an error to the client
            return server.responses.NotFound(server=server)

        # find who matched
        token = match.lastgroup
        # look up the handler
        handler = getattr(self, token)
        # invoke
        return handler(plexus=plexus, server=server, request=request, match=match)

    # metamethods
    def __init__(self, plexus, docroot, pfs, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the location of my document root so i can serve static assets
        self.docroot = docroot.discover()
        # attach it to the app's private filesystem
        pfs["ux"] = docroot

        # make a spec for the app engine
        spec = "store"
        # use the spec to build a name for my panel
        name = f"{plexus.pyre_name}.{spec}"
        # build the application store
        self.store = qed.ux.store(
            name=name,
            plexus=plexus,
            docroot=docroot,
            globalAliases=True,
        )
        # instantiate the {GraphQL} handler
        self.gql = GraphQL(plexus=plexus, dispatcher=self, store=self.store)

        # all done
        return

    # handlers
    def preview(self, server, match, **kwds):
        """
        Build a preview of a dataset
        """
        # unpack
        reader = match.group("preview_reader").split(".")
        uri = match.group("preview_uri")
        cell = match.group("preview_cell")
        shape = tuple(map(int, match.group("preview_shape").split(",")))
        zoom = int(match.group("preview_zoom"))
        view = tuple(map(int, match.group("preview_view").split(",")))

        # set up the reader configuration
        config = {
            "name": str(uuid.uuid1()),
            "uri": uri,
            "shape": shape,
        }
        # if {cell} is non-trivial
        if cell:
            # add it to the pile
            config["cell"] = cell

        # get the reader factory
        cls = functools.reduce(getattr, reader, qed.readers)
        # instantiate it
        reader = cls(**config)
        # get its first dataset
        data, *_ = reader.datasets
        # and the first registered channel
        channel, *_ = data.channels.values()
        # render the tile
        tile = data.render(
            channel=channel, zoom=(zoom, zoom), origin=(0, 0), shape=view
        )
        # and send it to the client
        return server.documents.BMP(server=server, bmp=memoryview(tile))

    def data(self, server, match, **kwds):
        """
        Handle a data request
        """
        # unpack
        viewport = int(match.group("data_viewport"))
        datasetName = match.group("data_dataset")
        channelName = match.group("data_channel")
        zoomSpec = match.group("data_zoom")
        zoom = tuple(map(int, zoomSpec.split("x")))
        spec = match.group("data_tile")
        origin = tuple(map(int, match.group("data_origin").split("x")))
        shape = tuple(map(int, match.group("data_shape").split("x")))

        # attempt to
        try:
            # get the tile
            tile = self.store.tile(
                viewport=viewport,
                channel=f"{datasetName}.{channelName}",
                zoom=zoom,
                origin=origin,
                shape=shape,
            )
        # if anything else goes wrong
        except Exception as error:
            # we have a problem
            chnl = journal.error("qed.ux.dispatch")
            # show me
            chnl.line(str(error))
            chnl.line(f"while fetching a tile of '{channelName}' from '{datasetName}'")
            chnl.line(f"with shape {shape} at {origin}")
            chnl.line(f"at zoom level {zoom}")
            # and flush
            chnl.log()
            # let the client know
            return server.responses.NotFound(server=server)

        # if all went well, we have a {tile} in memory; attempt to
        try:
            # build the response
            response = server.documents.BMP(server=server, bmp=memoryview(tile))
            # suggest a file name, in case the user wants to save the tile
            filename = f"{datasetName}.{channelName}.{zoomSpec}.{spec}.bmp"
            # encode it
            encoded = urllib.parse.quote(filename)
            # decorate it
            response.headers["Content-disposition"] = (
                f'attachment; filename="{filename}"; filename*={encoded}'
            )
            # grab a channel
            chnl = journal.debug("qed.ux.dispatch")
            # show me
            chnl.log(f"serving '{filename}'")
            # and return it
            return response
        # if anything goes wrong
        except Exception as error:
            # we have a problem
            chnl = journal.error("qed.ux.dispatch")
            # show me
            chnl.line(str(error))
            chnl.line(f"while generating a '{channelName}' tile of '{datasetName}'")
            chnl.line(f"with shape {shape} at {origin}")
            chnl.line(f"at zoom level {zoom}")
            # and flush
            chnl.log()
        # let the client know
        return server.responses.NotFound(server=server)

    def graphql(self, **kwds):
        """
        Handle a {graphql} request
        """
        # delegate to my {graphql} handler
        return self.gql.respond(store=self.store, **kwds)

    def profile(self, server, match, request, **kwds):
        """
        Handle a request for a dataset profile
        """
        # unpack
        name = match.group("profile_dataset")
        encoding = match.group("profile_format").lower()
        # the url contains the points of interest
        url = request.url
        # extract the query part
        _, query = url.split("?")
        # split the query
        tokens = query.split("&")
        # the first one is the closed path indicator
        tag, closed = tokens[0].split("=")
        # check
        if tag == "closed":
            # and parse
            closed = closed == "true"
        # points are separated by "&", coordinates by ","
        points = tuple(tuple(map(int, point.split(","))) for point in tokens[1:])

        # get the dataset
        dataset = self.store.dataset(name=name)
        # get the profile
        profile = dataset.profile(points=points, closed=closed)
        # form the file name
        filename = f"{dataset.pyre_name}.{encoding}"

        # get the document factory
        encoder = getattr(self, f"_profile{encoding.upper()}")
        # encode
        stream = encoder(dataset=dataset, profile=profile)
        # get the document factory
        document = getattr(server.documents, encoding.upper())
        # build the response
        response = document(server=server, value=stream)
        # decorate it
        response.headers["Content-disposition"] = f'attachment; filename="{filename}"'
        # and send it off
        return response

    # basic handlers
    def stop(self, plexus, server, **kwds):
        """
        The client is asking me to die
        """
        # log it
        plexus.info.log("shutting down")
        # and exit
        return server.documents.Exit(server=server, code=128 + signal.SIGQUIT)

    def document(self, plexus, server, request, **kwds):
        """
        The client requested a document from the {plexus} pfs
        """
        # form the uri
        uri = "/ux" + request.url
        # open the document and serve it
        return server.documents.File(uri=uri, server=server, application=plexus)

    def css(self, plexus, server, request, **kwds):
        """
        The client requested a document from the {plexus} pfs
        """
        # form the uri
        uri = "/ux" + request.url
        # open the document and serve it
        return server.documents.CSS(uri=uri, server=server, application=plexus)

    def jscript(self, plexus, server, request, **kwds):
        """
        The client requested a document from the {plexus} pfs
        """
        # form the uri
        uri = "/ux" + request.url
        # open the document and serve it
        return server.documents.Javascript(uri=uri, server=server, application=plexus)

    def favicon(self, plexus, server, request, **kwds):
        """
        The client requested the app icon
        """
        # we don't have one
        return server.responses.NotFound(server=server)

    def root(self, plexus, server, request, **kwds):
        """
        The client requested the root document
        """
        # form the uri
        uri = "/ux/{0.pyre_namespace}.html".format(plexus)
        # open the document and serve it
        return server.documents.File(uri=uri, server=server, application=plexus)

    # profile encoders
    def _profileCSV(self, dataset, profile):
        """
        Encode the {dataset} {profile} as CSV
        """
        # grab the important dataset channels
        channels = tuple(dataset.summary())
        # make a buffer so {csv} has someplace to write into
        buffer = io.StringIO()
        # make a writer
        writer = csv.writer(buffer)

        # get the headers
        headers = ("line", "sample") + tuple(channel.tag for channel in channels)
        # write them
        writer.writerow(headers)

        # go through the entries in the {profile}
        for entry in profile:
            # unpack
            line, sample, *pixel = entry
            # build the channel specific representations
            reps = tuple(channel.eval(*pixel) for channel in channels)
            # and record each one
            writer.writerow((line, sample) + reps)

        # all done
        return buffer.getvalue()

    # private data
    # recognizer fragments
    uuid = r"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}"
    pyreid = r"[^&?#:\s]+"
    zoom = r"-?\d+x-?\d+"
    origin = r"-?\d+x-?\d+"
    shape = r"\d+x\d+"
    # currently, only {csv} is supported
    profileFormat = r"(CSV)"

    # the app api
    regex = re.compile(
        "|".join(
            [
                # the data request recognizer
                r"/(?P<data>data/"
                + "/".join(
                    [
                        rf"(?P<data_viewport>\d+)",
                        rf"(?P<data_dataset>{pyreid})",
                        r"(?P<data_channel>\w+)",
                        rf"(?P<data_zoom>{zoom})",
                        rf"(?P<data_tile>(?P<data_origin>{origin})\+(?P<data_shape>{shape}))",
                    ]
                )
                + ")",
                # the preview generator
                r"/(?P<preview>preview\?"
                + "&".join(
                    [
                        # the reader
                        r"reader=(?P<preview_reader>[^&]+)",
                        # the uri
                        r"uri=(?P<preview_uri>[^&]+)",
                        # the data types
                        r"cell=(?P<preview_cell>[^&]*)",
                        # the shape
                        r"shape=(?P<preview_shape>[^&]+)",
                        # the zoom level
                        r"zoom=(?P<preview_zoom>[^&]+)",
                        # the view shape
                        r"view=(?P<preview_view>[^&]+)",
                    ]
                )
                + ")",
                # data profile requests
                r"/(?P<profile>profile/"
                + "/".join(
                    [
                        rf"(?P<profile_format>{profileFormat})",
                        rf"(?P<profile_dataset>{pyreid})",
                    ]
                )
                + ")",
                # graphql requests
                r"/(?P<graphql>graphql)",
                # the kill command
                r"/(?P<stop>stop)",
                # document requests
                r"/(?P<css>.+\.css)",
                r"/(?P<jscript>.+\.js)",
                r"/(?P<document>(graphics/.+)|(fonts/.+)|(figures/.+))",
                r"/(?P<favicon>favicon.ico)",
                # everything else gets the app page; see the {root} resolver above
                r"/(?P<root>.*)",
            ]
        )
    )


# end of file
