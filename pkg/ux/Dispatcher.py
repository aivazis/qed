# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import csv
import functools
import io
import re
import signal
import time
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

        # the ledger of tile requests that have been parked and not yet answered, and the
        # counter that gives each one a name. a tile that misses the cache parks its
        # connection and waits for a worker; nothing else in the server knows how many are
        # waiting or for how long, so a request that is never delivered is invisible -- and
        # a browser whose connection pool fills with them cannot ask for anything at all,
        # which looks exactly like a server that has stopped serving
        self._parked = {}
        self._sequence = 0

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
        # construction is passive; a preview exists to produce pixels, so make first contact
        reader.open()
        # get its first dataset
        data, *_ = reader.datasets
        # if the requested view oversteps the raster, the native pipeline would crash
        if not self._dataInBounds(
            dataset=data, zoom=(zoom, zoom), origin=(0, 0), shape=view
        ):
            # the client derives the preview geometry from the product metadata, so an
            # overstep is a bug in whoever built the request
            firewall = journal.firewall("qed.ux.dispatch")
            # complain
            firewall.line(f"preview out of bounds")
            firewall.line(f"while previewing '{uri}'")
            firewall.line(f"with view {view} at zoom {zoom}")
            firewall.line(f"of a dataset with shape {data.shape}")
            # flush
            firewall.log()
            # and refuse, in case firewalls aren't fatal
            return server.responses.NotFound(server=server)
        # get the first registered channel
        channel, *_ = data.channels.values()
        # render the tile
        tile = data.render(
            channel=channel, zoom=(zoom, zoom), origin=(0, 0), shape=view
        )
        # and send it to the client
        return server.documents.BMP(server=server, bmp=memoryview(tile))

    def peek(self, server, request, match, **kwds):
        """
        Render a tile for the peek window, on this thread

        The peek follows the cursor, so it asks for a small tile at an arbitrary origin many
        times a second and never asks for the same one twice. Those renders have no business
        going to a crew: each would park a connection, occupy a worker, and leave behind a
        cached payload holding a file descriptor that nothing will ever read again. They are
        small and quick, so they are drawn here and forgotten
        """
        # unpack
        viewport = int(match.group("peek_viewport"))
        datasetName = match.group("peek_dataset")
        channelName = match.group("peek_channel")
        zoomSpec = match.group("peek_zoom")
        zoom = tuple(map(int, zoomSpec.split("x")))
        spec = match.group("peek_tile")
        origin = tuple(map(int, match.group("peek_origin").split("x")))
        shape = tuple(map(int, match.group("peek_shape").split("x")))
        # draw it here and now; nothing about this tile is worth keeping
        return self._dataInline(
            server=server,
            viewport=viewport,
            datasetName=datasetName,
            channelName=channelName,
            zoomSpec=zoomSpec,
            zoom=zoom,
            spec=spec,
            origin=origin,
            shape=shape,
        )

    def data(self, server, request, match, **kwds):
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
        # bundle the request details so the helpers can share them
        tilespec = {
            "viewport": viewport,
            "datasetName": datasetName,
            "channelName": channelName,
            "zoomSpec": zoomSpec,
            "zoom": zoom,
            "spec": spec,
            "origin": origin,
            "shape": shape,
        }

        # diagnostic: when the {qed.ux.tiles} channel is active (off by default), each tile
        # request gets one compact line -- client, session, outcome, and timings
        tiles = journal.debug("qed.ux.tiles")
        # capture the request clocks only when someone is listening, so the common inactive
        # case pays nothing; per-request captures, unlike shared named timers, survive the
        # concurrency of the deferred path
        clocks = (time.perf_counter(), time.process_time()) if tiles.active else None
        # name this request, so its arrival and its outcome can be paired in the log; a
        # request that arrives and never completes is otherwise indistinguishable from one
        # that never arrived, and those are opposite faults
        self._sequence += 1
        sequence = self._sequence
        # bind the diagnostic to this request; a no-op while the channel is inactive
        record = functools.partial(
            self._logTile,
            tiles=tiles,
            clocks=clocks,
            sequence=sequence,
            request=request,
            viewport=viewport,
            dataset=datasetName,
            channel=channelName,
            zoom=zoom,
            origin=origin,
            shape=shape,
        )

        # say that it got here; everything below this point can fail to produce a line, so
        # this is the only evidence that the request existed at all
        record(code=None, via="arrive")

        # attempt to
        try:
            # get the view behind the request
            view = self.store.view(viewport=viewport)
        # if the viewport is unknown
        except IndexError:
            # let the inline path complain
            response = self._dataInline(server=server, **tilespec)
            # record the outcome
            record(code=response.code, via="inline")
            # and pass it along
            return response

        # get the dataset behind the request; the render machinery trusts its callers, so a
        # tile that hangs over the edge of the raster crashes the native pipeline
        dataset = view.dataset
        # if there is a dataset to check against and the request oversteps it
        if dataset is not None and not self._dataInBounds(
            dataset=dataset, zoom=zoom, origin=origin, shape=shape
        ):
            # our own client computes its tile grid from the dataset shape this server
            # published, so an overstep is a bug in whoever built the request
            firewall = journal.firewall("qed.ux.dispatch")
            # complain
            firewall.line(f"tile out of bounds")
            firewall.line(
                f"while fetching a tile of '{channelName}' from '{datasetName}'"
            )
            firewall.line(f"with shape {shape} at {origin}, zoom {zoom}")
            firewall.line(f"of a dataset with shape {dataset.shape}")
            # flush
            firewall.log()
            # record the refusal
            record(code=404, via="refused")
            # and refuse, in case firewalls aren't fatal
            return server.responses.NotFound(server=server)

        # look for the fleet of tile rendering teams; only the qed flavor of the server has one
        fleet = getattr(server, "fleet", None)
        # if there is no fleet
        if fleet is None:
            # render on the spot
            response = self._dataInline(server=server, **tilespec)
            # record the outcome
            record(code=response.code, via="inline")
            # and pass it along
            return response

        # when a stack is pinned to a single member, the view swaps in the member's own
        # dataset; its render belongs to the member reader, which the task recipe cannot
        # name, so it stays on the inline path
        if isinstance(view.reader, qed.stacks.stack) and not isinstance(
            view.dataset, qed.stacks.dataset
        ):
            # render on the spot
            response = self._dataInline(server=server, **tilespec)
            # record the outcome
            record(code=response.code, via="inline")
            # and pass it along
            return response

        # attempt to
        try:
            # describe the tile as a task that can travel to a worker
            task = qed.nexus.tile(
                view=view,
                channel=f"{datasetName}.{channelName}",
                zoom=zoom,
                origin=origin,
                shape=shape,
                workspace=self.store.workspace,
            )
        # if the description cannot be built, e.g. there is no dataset selection
        except Exception:
            # fall back to the inline path, which knows how to complain
            response = self._dataInline(server=server, **tilespec)
            # record the outcome
            record(code=response.code, via="inline")
            # and pass it along
            return response

        # a cached render of this exact specification can be served on the spot
        cached = fleet.lookup(task=task)
        # if there is one
        if cached is not None:
            # record the hit
            record(code=200, via="hit")
            # map it; the response document holds the view until the payload is on the wire
            return self._dataDocument(
                server=server,
                tile=cached.view(),
                datasetName=datasetName,
                channelName=channelName,
                zoomSpec=zoomSpec,
                zoom=zoom,
                spec=spec,
                origin=origin,
                shape=shape,
            )

        # make a placeholder response that parks the connection
        deferred = server.deferred()
        # build the delivery callback
        callback = functools.partial(
            self._dataDeliver,
            server=server,
            deferred=deferred,
            record=record,
            **tilespec,
        )

        # if the client hangs up while the tile is queued
        def abandoned():
            # withdraw the request
            fleet.revoke(task=task, callback=callback)
            # and record the departure
            record(code=499, via="hangup")
            # all done
            return

        # arm the hangup hook
        deferred.abandoned = abandoned
        # queue the task with the team dedicated to its data source
        fleet.render(task=task, callback=callback)
        # and hand the placeholder to the server
        return deferred

    def _dataInBounds(self, dataset, zoom, origin, shape):
        """
        Check that the tile at {origin}+{shape} lies within {dataset} at the given {zoom}

        Tile requests are in zoomed coordinates: the render pipeline scales both the origin
        and the shape by the stride, so the source footprint of the tile is what must fit
        """
        # go through the axes
        for level, start, extent, bound in zip(zoom, origin, shape, dataset.shape):
            # a tile of empty or negative extent is meaningless
            if extent <= 0:
                # reject
                return False
            # the recognizer admits signed zoom levels, but the render pipeline only knows how
            # to decimate; a negative level would produce a fractional stride and die deep in
            # the extension, so refuse it here
            if level < 0:
                # reject
                return False
            # the stride the render pipeline derives from the zoom level
            stride = 2**level
            # the source footprint must start within the raster
            if start < 0:
                # reject
                return False
            # and end within it
            if (start + extent) * stride > bound:
                # reject
                return False
        # all axes check out
        return True

    def _profileInBounds(self, dataset, points):
        """
        Check that every profile point lies within {dataset}

        Points arrive as (line, sample) pairs, matching the dataset shape; the native profiler
        reads each interpolated pixel individually, so every point must name a real cell
        """
        # go through the points
        for point in points:
            # a point must have exactly one coordinate per axis
            if len(point) != len(dataset.shape):
                # reject
                return False
            # go through its coordinates
            for coordinate, extent in zip(point, dataset.shape):
                # each must name a cell within the raster
                if coordinate < 0 or coordinate >= extent:
                    # reject
                    return False
        # all points check out
        return True

    def _dataInline(
        self,
        server,
        viewport,
        datasetName,
        channelName,
        zoomSpec,
        zoom,
        spec,
        origin,
        shape,
    ):
        """
        Render a tile synchronously and wrap it up as a response document
        """
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

        # if all went well, we have a {tile} in memory; wrap it up
        return self._dataDocument(
            server=server,
            tile=memoryview(tile),
            datasetName=datasetName,
            channelName=channelName,
            zoomSpec=zoomSpec,
            zoom=zoom,
            spec=spec,
            origin=origin,
            shape=shape,
        )

    def _dataDeliver(
        self,
        result,
        error,
        server,
        deferred,
        viewport,
        datasetName,
        channelName,
        zoomSpec,
        zoom,
        spec,
        origin,
        shape,
        record=None,
    ):
        """
        The team has reported the outcome of a tile task; resolve the parked response
        """
        # if the task took its crew member down, the task itself may be the killer, e.g. a
        # request that crashes the native pipeline; retrying it inline would gamble the server
        if isinstance(error, qed.nexus.exceptions.Casualty):
            # tell me
            chnl = journal.warning("qed.nexus.tiles")
            # what happened
            chnl.line(str(error))
            chnl.line(f"while rendering a '{channelName}' tile of '{datasetName}'")
            chnl.line(f"with shape {shape} at {origin}")
            chnl.line(f"the task is suspect; refusing to retry it in the server")
            # and flush
            chnl.log()
            # record the casualty
            if record is not None:
                record(code=404, via="crew")
            # let the client know; it can always ask again
            return deferred.resolve(response=server.responses.NotFound(server=server))
        # if the worker could not produce the tile for a benign reason
        if error is not None:
            # tell me
            chnl = journal.warning("qed.nexus.tiles")
            # what happened
            chnl.line(str(error))
            chnl.line(f"while rendering a '{channelName}' tile of '{datasetName}'")
            chnl.line(f"with shape {shape} at {origin}")
            chnl.line(f"falling back to the inline renderer")
            # and flush
            chnl.log()
            # render on the spot so reconstruction gaps degrade gracefully
            response = self._dataInline(
                server=server,
                viewport=viewport,
                datasetName=datasetName,
                channelName=channelName,
                zoomSpec=zoomSpec,
                zoom=zoom,
                spec=spec,
                origin=origin,
                shape=shape,
            )
            # record the fallback outcome
            if record is not None:
                record(code=response.code, via="inline")
            # and deliver whatever came out
            return deferred.resolve(response=response)

        # on success, the tile arrives parked in a spool; map its payload
        view = result.view()
        # and wrap it up as a document
        response = self._dataDocument(
            server=server,
            tile=view,
            datasetName=datasetName,
            channelName=channelName,
            zoomSpec=zoomSpec,
            zoom=zoom,
            spec=spec,
            origin=origin,
            shape=shape,
        )
        # record the delivery
        if record is not None:
            record(code=200, via="crew")
        # deliver it; the write to the client happens within
        status = deferred.resolve(response=response)
        # the payload is on the wire; release my mapping of it. the spool itself is owned by
        # the team, which releases it once every subscriber has been served
        view.close()
        # all done
        return status

    def _dataDocument(
        self,
        server,
        tile,
        datasetName,
        channelName,
        zoomSpec,
        zoom,
        spec,
        origin,
        shape,
    ):
        """
        Wrap a rendered {tile} in a BMP response document
        """
        # attempt to
        try:
            # build the response
            response = server.documents.BMP(server=server, bmp=tile)
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

    def schema(self, server, **kwds):
        """
        Serve the GraphQL schema as SDL so external clients can retrieve it
        """
        # render the schema as SDL text
        document = qed.gql.sdl()
        # wrap it in a literal text response
        response = server.documents.Literal(server=server, value=document)
        # mark it as plain text
        response.headers["Content-Type"] = "text/plain; charset=utf-8"
        # and send it off
        return response

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
        # a profile reads the product on the spot, so a dataset left metadata-only by a
        # survey has to open its file before it can answer
        dataset = self.store.realize(dataset=dataset)
        # if any point of interest lies outside the raster, the per-pixel reads would crash
        if not self._profileInBounds(dataset=dataset, points=points):
            # the client clips its anchors to the dataset shape, so an overstep is a bug in
            # whoever built the request
            firewall = journal.firewall("qed.ux.dispatch")
            # complain
            firewall.line(f"profile point out of bounds")
            firewall.line(f"while profiling '{name}'")
            firewall.line(f"along {points}")
            firewall.line(f"of a dataset with shape {dataset.shape}")
            # flush
            firewall.log()
            # and refuse, in case firewalls aren't fatal
            return server.responses.NotFound(server=server)
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
        response.headers["content-disposition"] = f'attachment; filename="{filename}"'
        # and send it off
        return response

    # basic handlers
    def events(self, server, **kwds):
        """
        Open a server-sent event stream so the client receives live state-change notifications
        """
        # hand back a streaming response; the server subscribes this connection to its hub
        return server.eventStream(server=server)

    def stop(self, plexus, server, **kwds):
        """
        The client is asking me to die
        """
        # log it
        plexus.info.log("shutting down")
        # and exit
        return server.documents.Exit(server=server, exitCode=128 + signal.SIGQUIT)

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

    # debugging and logging support
    @staticmethod
    def _tileClient(agent):
        """
        Map a {User-Agent} string to a short client label for the tile journal
        """
        # our headless probe marks itself explicitly
        if "qed-probe" in agent:
            return "probe"
        # edge identifies with {Edg}, but also carries {Chrome} and {Safari}, so test it first
        if "Edg" in agent:
            return "edge"
        # chrome carries {Safari} too, so it must come before the safari test
        if "Chrome" in agent or "Chromium" in agent:
            return "chrome"
        # safari last
        if "Safari" in agent:
            return "safari"
        # anything else, including our probe's fallback
        return "other"

    def _logTile(
        self,
        tiles,
        clocks,
        sequence,
        request,
        viewport,
        dataset,
        channel,
        zoom,
        origin,
        shape,
        code,
        via,
    ):
        """
        Record one tile request on the {qed.ux.tiles} diagnostic channel, when it is active

        Called twice per request: once on arrival, and once with the outcome. The pair is
        tied together by {sequence}, so a request that arrived and never finished can be
        found by looking for a name that appears once
        """
        # the ledger is kept whatever the channel is doing, since it is the only place that
        # knows how many requests are waiting; it costs one dictionary operation per request
        if via == "arrive":
            # remember when this one got here and what it was after
            self._parked[sequence] = (time.time(), f"{dataset}.{channel} at {origin}")
        else:
            # every other outcome retires it, including the ones that fail
            self._parked.pop(sequence, None)
        # nothing further unless someone has turned the channel on; this guard keeps the
        # gathering and formatting below -- the only real cost -- out of the hot path in the
        # common inactive case
        if not tiles.active:
            return
        # read the request clocks; {dt} is elapsed latency, including any time spent queued
        # and rendered in a worker, while {cpu} is this server's own compute
        dt = (time.perf_counter() - clocks[0]) * 1000 if clocks else 0.0
        cpu = (time.process_time() - clocks[1]) * 1000 if clocks else 0.0
        # identify the requesting client from its user agent
        try:
            agent = request.headers["User-Agent"]
        except (KeyError, TypeError):
            agent = ""
        client = self._tileClient(agent=agent)
        # the session token rides in the query string; it is what pierces the tile {Mosaic} memo
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(request.url).query)
        session = query.get("session", ["?"])[0]
        # the current shared look-at, for context on whether this tile sits near the viewport
        try:
            center = self.store.view(viewport=viewport).center
            lookAt = (round(center.row), round(center.col))
        except (IndexError, AttributeError, TypeError):
            lookAt = None
        # how many requests are waiting, and how long the most patient of them has waited;
        # a queue that grows and an age that never resets are the signature of tiles that
        # are being accepted and never answered
        waiting = len(self._parked)
        oldest = (
            f"{time.time() - min(when for when, _ in self._parked.values()):.1f}s"
            if self._parked
            else "-"
        )
        # one compact, greppable line
        tiles.log(
            f"seq={sequence} client={client} vp={viewport} {dataset}.{channel} "
            f"zoom={zoom} origin={origin[0]}x{origin[1]} "
            f"shape={shape[0]}x{shape[1]} session={session[:8]} "
            f"lookAt={lookAt} code={code if code is not None else '-'} via={via} "
            f"dt={dt:.1f}ms cpu={cpu:.1f}ms parked={waiting} oldest={oldest}"
        )

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
                        rf"(?P<data_channel>\w+)",
                        rf"(?P<data_zoom>{zoom})",
                        rf"(?P<data_tile>(?P<data_origin>{origin})\+(?P<data_shape>{shape}))",
                    ]
                )
                + ")",
                # the peek window's tiles; a route of their own so those renders can be kept
                # off the crews and out of the cache
                r"/(?P<peek>peek/"
                + "/".join(
                    [
                        rf"(?P<peek_viewport>\d+)",
                        rf"(?P<peek_dataset>{pyreid})",
                        rf"(?P<peek_channel>\w+)",
                        rf"(?P<peek_zoom>{zoom})",
                        rf"(?P<peek_tile>(?P<peek_origin>{origin})\+(?P<peek_shape>{shape}))",
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
                # the schema in SDL form, for external clients
                r"/(?P<schema>schema)",
                # the live server-sent event stream
                r"/(?P<events>events)",
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
