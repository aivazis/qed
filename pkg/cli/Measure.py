# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import concurrent.futures
import csv
import journal
import json
import os
import subprocess
import time
import urllib.error
import urllib.request

# support
import qed


# declaration
class Measure(qed.shells.command, family="qed.cli.measure"):
    """
    Measure the cost structure of tile generation

    The program is laid out in doc/performance.md: fit the per-request cost to the model
    {time = a + b·pixels} on two independent sweep axes, read the wall-cpu gap to classify
    the marginal cost, and let the parallelism conclusion fall out of the numbers
    """

    # sweep restrictions
    only = qed.properties.strings()
    only.default = []
    only.doc = "restrict the sweep to the datasets of these readers; empty sweeps all"

    channels = qed.properties.strings()
    channels.default = []
    channels.doc = "restrict the sweep to these channels; empty sweeps all"

    # sweep geometry
    shapes = qed.properties.tuple(schema=qed.properties.int())
    shapes.default = (8, 12)
    shapes.doc = (
        "the half open range of tile shape exponents; (8,12) sweeps 256 through 2048"
    )

    zooms = qed.properties.tuple(schema=qed.properties.int())
    zooms.default = (0, 3)
    zooms.doc = "the half open range of zoom levels; higher zoom pulls a larger source footprint"

    origin = qed.properties.tuple(schema=qed.properties.int())
    origin.default = (0, 0)
    origin.doc = "the tile origin, in decimated coordinates"

    # measurement discipline
    trials = qed.properties.int()
    trials.default = 3
    trials.doc = "the number of repetitions of each measurement point"

    cache = qed.properties.str()
    cache.default = "warm"
    cache.doc = "the cache state label stamped on each record"

    cold = qed.properties.bool()
    cold.default = False
    cold.doc = "rerun each point in a fresh process, defeating the in-process caches"

    output = qed.properties.str()
    output.default = "measurements.csv"
    output.doc = "the file that accumulates the measurement records"

    # swarm configuration
    clients = qed.properties.tuple(schema=qed.properties.int())
    clients.default = (1, 2, 4, 8)
    clients.doc = "the sequence of client concurrency levels to sweep"

    team = qed.properties.int()
    team.default = 4
    team.doc = "the size of the rendering team of the launched server"

    port = qed.properties.int()
    port.default = 8181
    port.doc = "the port of the launched server"

    tiles = qed.properties.int()
    tiles.default = 64
    tiles.doc = "the number of distinct tiles in the swarm workload"

    # interface
    @qed.export(tip="sweep tile generation and record the cost of each request")
    def tile(self, plexus, **kwds):
        """
        Sweep tile generation over shape, zoom, and channel, recording the wall and cpu time
        of each request as one flat record per trial
        """
        # in cold mode
        if self.cold:
            # each measurement point runs in a fresh process
            return self._resweep(plexus=plexus)
        # otherwise, run the sweep in this process
        return self._sweep(plexus=plexus)

    @qed.export(tip="fit the recorded measurements to the cost model")
    def fit(self, plexus, **kwds):
        """
        Fit the accumulated records to {time = a + b·pixels} on both sweep axes and report
        the fixed cost, the marginal cost, and the wall-cpu character of each group
        """
        # make a channel
        channel = journal.info("qed.measure.fit")
        # load the accumulated records
        records = self._load()
        # if there is nothing to fit
        if not records:
            # complain
            error = journal.error("qed.measure.fit")
            error.log(f"no records in '{self.output}'; run 'qed measure tile' first")
            # and bail
            return 1
        # the shape axis isolates the per-output-pixel cost
        self._report(channel=channel, records=records, axis="shape")
        # the zoom axis isolates the per-source-cell cost
        self._report(channel=channel, records=records, axis="zoom")
        # flush the report
        channel.log()
        # all done
        return 0

    @qed.export(tip="measure concurrent tile serving against a launched server")
    def swarm(self, plexus, **kwds):
        """
        Launch the qed server, fire concurrent tile clients at it in increasing numbers, and
        record the throughput at each concurrency level

        This is the validation half of the program: the single-process sweeps forecast the
        parallel ceiling through Amdahl's law, and the swarm measures the actual speedup
        """
        # make a channel
        channel = journal.info("qed.measure.swarm")
        # pick the first target the restrictions allow
        first = next(self._targets(plexus=plexus), None)
        # if there is none
        if first is None:
            # complain
            error = journal.error("qed.measure.swarm")
            error.log(
                "no dataset to measure; check the configuration and the restrictions"
            )
            # and bail
            return 1
        # unpack the target
        reader, dataset, name, _ = first
        # the workload geometry: the smallest configured tile at the lowest configured zoom
        span = 2 ** self.shapes[0]
        zoom = self.zooms[0]
        # lay out the workload as a grid of distinct tiles; identical in-flight requests
        # collapse in the team workplan, so distinct tiles are essential to load the workers
        origins = list(self._grid(dataset=dataset, span=span, zoom=zoom))
        # if the raster cannot hold even one tile
        if not origins:
            # complain
            error = journal.error("qed.measure.swarm")
            error.log(
                f"'{dataset.pyre_name}' cannot fit a {span}x{span} tile at zoom {zoom}"
            )
            # and bail
            return 1
        # if the raster ran out of room before the workload filled up
        if len(origins) < self.tiles:
            # say so, so a smaller workload is never mistaken for the requested one
            channel.line(f"workload truncated to {len(origins)} of {self.tiles} tiles")
        # assemble the tile request urls
        urls = [
            f"http://127.0.0.1:{self.port}"
            f"/data/0/{dataset.pyre_name}/{name}/{zoom}x{zoom}/{r}x{c}+{span}x{span}"
            for r, c in origins
        ]
        # launch the server
        process, log = self._launch(reader=reader)
        # from here on, the server must come down no matter what happens
        try:
            # wait for it to accept connections
            if not self._ready():
                # if it never came up, complain
                error = journal.error("qed.measure.swarm")
                error.log(
                    f"the server on port {self.port} never came up; see '{log.name}'"
                )
                # and bail
                return 1
            # the tile path resolves its reader through server side view state, so drive the
            # selections the way the client would
            self._select(reader=reader, channel=name)
            # warm up with one full pass so every concurrency level sees the same cache state
            self._batch(urls=urls, workers=max(self.clients))
            # the collected results, one entry per concurrency level
            results = []
            # sweep the concurrency levels
            for workers in self.clients:
                # fire the workload
                elapsed, latencies, failures = self._batch(urls=urls, workers=workers)
                # failed requests void the level; say so rather than reporting on the rest
                if failures:
                    # complain
                    warning = journal.warning("qed.measure.swarm")
                    warning.log(f"{failures} requests failed at {workers} clients")
                # the aggregate rate, counting only delivered tiles
                rate = len(latencies) / (elapsed / 1000) if elapsed > 0 else 0
                # collect the level
                results.append((workers, elapsed, rate, latencies, failures))
                # show me
                channel.line(
                    f"{workers:4} clients: {rate:6.1f} tiles/s, batch {elapsed:.0f} ms"
                )
        # no matter how the sweep went
        finally:
            # bring the server down
            self._stop(process=process, log=log)
        # persist and report the levels
        self._tabulate(
            channel=channel,
            dataset=dataset,
            name=name,
            zoom=zoom,
            span=span,
            count=len(urls),
            results=results,
        )
        # flush the report
        channel.log()
        # all done
        return 0

    # implementation details: the single process sweep
    def _sweep(self, plexus):
        """
        Run the sweep in this process, appending one record per trial to the output file
        """
        # make a channel
        channel = journal.info("qed.measure.tile")
        # the host label that lets records from different machines share a file
        host = self.pyre_host.nickname
        # open the record sink
        stream, writer = self._sink()
        # the readers whose open costs have been reported
        seen = set()
        # go through the targets
        for reader, dataset, name, pipeline in self._targets(plexus=plexus):
            # the first time a reader shows up
            if reader.pyre_name not in seen:
                # mark it
                seen.add(reader.pyre_name)
                # read the open time costs its constructor accumulated
                discovery = qed.timers.wall(
                    f"qed.profiler.discovery.{reader.pyre_name}"
                ).ms()
                stats = qed.timers.wall(f"qed.profiler.stats.{reader.pyre_name}").ms()
                # and report them; they are the per-dataset part of the fixed cost
                channel.line(
                    f"{reader.pyre_name}: discovery {discovery:.1f} ms, stats {stats:.1f} ms"
                )
            # the cell type label comes from the family of the datatype
            cell = dataset.cell.pyre_family().rsplit(".", 1)[-1]
            # go through the measurement points
            for span, zoom in self._points(dataset=dataset):
                # show me
                channel.line(
                    f"  {dataset.pyre_name}.{name}: {span}x{span} @ zoom {zoom}"
                )
                # repeat the point
                for trial in range(self.trials):
                    # read the clocks
                    wall = time.perf_counter()
                    cpu = time.process_time()
                    # render the tile through the full pipeline, encoder included
                    dataset.render(
                        channel=pipeline,
                        zoom=(zoom, zoom),
                        origin=tuple(self.origin),
                        shape=(span, span),
                    )
                    # read the clocks again
                    wall = (time.perf_counter() - wall) * 1000
                    cpu = (time.process_time() - cpu) * 1000
                    # the two denominators: output pixels drawn, source cells touched
                    pixels = span * span
                    cells = pixels * 4**zoom
                    # record the trial
                    writer.writerow(
                        (
                            "tile",
                            host,
                            dataset.pyre_name,
                            name,
                            cell,
                            zoom,
                            span,
                            pixels,
                            cells,
                            self.cache,
                            trial,
                            f"{wall:.3f}",
                            f"{cpu:.3f}",
                        )
                    )
        # flush the progress report
        channel.log()
        # and the records
        stream.close()
        # all done
        return 0

    def _resweep(self, plexus):
        """
        Rerun each measurement point in a fresh process, so the libhdf5 chunk cache, the page
        buffer, and the open time statistics touch start from scratch every time

        The OS page cache survives process boundaries, so these records are labeled 'fresh',
        not 'cold'; truly cold numbers require evicting the page cache as well
        """
        # make a channel
        channel = journal.info("qed.measure.tile")
        # go through the targets
        for reader, dataset, name, _ in self._targets(plexus=plexus):
            # and the measurement points
            for span, zoom in self._points(dataset=dataset):
                # recover the shape exponent
                exponent = span.bit_length() - 1
                # narrow the sweep to this one point and hand it to a fresh process
                cmd = [
                    "qed",
                    "measure",
                    "tile",
                    # the configuration may prefer the web shell; the child is a CLI run
                    "--shell=script",
                    f"--only={reader.pyre_name}",
                    f"--channels={name}",
                    f"--shapes={exponent},{exponent + 1}",
                    f"--zooms={zoom},{zoom + 1}",
                    f"--origin={self.origin[0]},{self.origin[1]}",
                    "--trials=1",
                    "--cache=fresh",
                    "--cold=no",
                    f"--output={self.output}",
                ]
                # show me
                channel.line(
                    f"fresh: {dataset.pyre_name}.{name}: {span}x{span} @ zoom {zoom}"
                )
                # launch and wait
                got = subprocess.run(cmd)
                # if the point failed
                if got.returncode != 0:
                    # a missing point silently skews the fit, so make it loud
                    warning = journal.warning("qed.measure.tile")
                    warning.log(
                        f"point failed: {dataset.pyre_name}.{name} "
                        f"{span}x{span} @ zoom {zoom}"
                    )
        # flush the progress report
        channel.log()
        # all done
        return 0

    def _targets(self, plexus):
        """
        Enumerate the (reader, dataset, channel name, pipeline) tuples the restrictions allow
        """
        # the reader restriction
        only = set(self.only)
        # the channel restriction
        channels = set(self.channels)
        # the plexus hands its readers to the ux store at construction, so the store is the
        # authority on the connected data sources; without ux support there is nothing to do
        ux = plexus._ux
        # if it is missing
        if ux is None:
            # there are no sources to measure
            return
        # go through the connected readers
        for reader in ux.store.sources:
            # stacks render aggregates, whose sweep needs the membership axis; leave them
            # out until the measurement program takes that on
            if isinstance(reader, qed.stacks.stack):
                # by skipping them
                continue
            # honor the reader restriction
            if only and reader.pyre_name not in only:
                # by skipping everybody else
                continue
            # construction is passive; measuring needs the data, so make first contact,
            # which also charges the discovery and stats timers this panel reports
            reader.open()
            # go through the reader's datasets
            for dataset in reader.datasets:
                # and each dataset's channels
                for name in dataset.channels.keys():
                    # honor the channel restriction
                    if channels and name not in channels:
                        # by skipping everybody else
                        continue
                    # resolve the visualization pipeline
                    pipeline = dataset.channel(name=name)
                    # and publish the target
                    yield reader, dataset, name, pipeline
        # all done
        return

    def _points(self, dataset):
        """
        Enumerate the (span, zoom) measurement points that fit within {dataset}
        """
        # unpack the raster shape
        rows, cols = dataset.shape
        # go through the tile shape exponents
        for exponent in range(*self.shapes):
            # form the square tile extent
            span = 2**exponent
            # go through the zoom levels
            for zoom in range(*self.zooms):
                # a tile that hangs over the raster edge crashes the native pipeline
                if (self.origin[0] + span) * 2**zoom > rows or (
                    self.origin[1] + span
                ) * 2**zoom > cols:
                    # so skip points that don't fit
                    continue
                # publish the point
                yield span, zoom
        # all done
        return

    def _sink(self):
        """
        Open the record file for appending, writing the header on first contact
        """
        # check whether this is first contact
        fresh = not os.path.exists(self.output)
        # open the file for appending, so sweeps accumulate
        stream = open(self.output, mode="a", newline="")
        # make a writer
        writer = csv.writer(stream)
        # on first contact
        if fresh:
            # write the header
            writer.writerow(self._tileHeaders)
        # hand back both, so the caller can close the stream
        return stream, writer

    # implementation details: the fit
    def _load(self):
        """
        Load the accumulated records, coercing the numeric fields
        """
        # the pile of records
        records = []
        # if the record file is missing
        if not os.path.exists(self.output):
            # there is nothing to load
            return records
        # otherwise, open it
        with open(self.output, mode="r", newline="") as stream:
            # go through the rows
            for row in csv.DictReader(stream):
                # coerce the sweep coordinates
                for field in ("zoom", "span", "pixels", "cells", "trial"):
                    # in place
                    row[field] = int(row[field])
                # and the timings
                for field in ("wall_ms", "cpu_ms"):
                    # in place
                    row[field] = float(row[field])
                # collect the record
                records.append(row)
        # all done
        return records

    def _report(self, channel, records, axis):
        """
        Fit each group of records along the given sweep {axis} and report the parameters
        """
        # the shape axis holds zoom fixed and varies the output size
        if axis == "shape":
            # so the denominator is output pixels
            denominator = "pixels"
            # grouped at constant zoom
            grouping = ("dataset", "channel", "zoom", "cache")
            # under this banner
            title = "per output pixel, at fixed zoom"
        # the zoom axis holds the output size fixed and varies the source footprint
        else:
            # so the denominator is source cells
            denominator = "cells"
            # grouped at constant tile shape
            grouping = ("dataset", "channel", "span", "cache")
            # under this banner
            title = "per source cell, at fixed tile shape"
        # bin the records
        groups = {}
        # by their group key
        for record in records:
            # assembled from the grouping fields
            key = tuple(record[field] for field in grouping)
            # and pile them up
            groups.setdefault(key, []).append(record)
        # sign on
        channel.line(f"{title}:")
        # go through the groups
        for key, members in sorted(groups.items(), key=lambda item: str(item[0])):
            # assemble the sample
            points = [(member[denominator], member["wall_ms"]) for member in members]
            # a line needs at least two distinct sizes
            if len({x for x, _ in points}) < 2:
                # so skip degenerate groups
                continue
            # fit the cost model
            a, b, r2 = self._regress(points=points)
            # measure the wall-cpu gap: the fraction of wall time spent off the cpu
            gap = sum(
                (member["wall_ms"] - member["cpu_ms"]) / member["wall_ms"]
                for member in members
                if member["wall_ms"] > 0
            ) / len(members)
            # label the group
            label = ", ".join(f"{field}={value}" for field, value in zip(grouping, key))
            # and report
            channel.line(f"  {label}:")
            channel.line(f"    a: {a:.3f} ms fixed cost per request")
            # a positive slope has a meaningful throughput reading
            if b > 0:
                # so include it
                channel.line(
                    f"    b: {b * 1e6:.1f} ns per unit ({1 / (b * 1000):.1f} M/s)"
                )
            # a vanishing or negative slope means the fixed cost dominates at these sizes
            else:
                # report it raw
                channel.line(f"    b: {b * 1e6:.1f} ns per unit")
            # close with the fit quality and the wall-cpu character
            channel.line(f"    r2: {r2:.3f}, wall-cpu gap: {gap:.0%}")
        # all done
        return

    def _regress(self, points):
        """
        Least squares fit of {points} to the line {y = a + b·x}
        """
        # the sample size
        n = len(points)
        # the means
        mx = sum(x for x, _ in points) / n
        my = sum(y for _, y in points) / n
        # the second moments
        sxx = sum((x - mx) ** 2 for x, _ in points)
        syy = sum((y - my) ** 2 for _, y in points)
        sxy = sum((x - mx) * (y - my) for x, y in points)
        # the slope
        b = sxy / sxx
        # the intercept
        a = my - b * mx
        # the quality of the fit, guarded against a constant sample
        r2 = sxy * sxy / (sxx * syy) if sxx > 0 and syy > 0 else 0
        # all done
        return a, b, r2

    # implementation details: the swarm
    def _grid(self, dataset, span, zoom):
        """
        Lay out up to {tiles} distinct in-bounds tile origins, in decimated coordinates
        """
        # unpack the raster shape
        rows, cols = dataset.shape
        # reduce it to the decimated extents at this zoom
        decRows = rows >> zoom
        decCols = cols >> zoom
        # the running count
        count = 0
        # walk the raster in tile sized steps
        for r in range(0, decRows - span + 1, span):
            # in row major order
            for c in range(0, decCols - span + 1, span):
                # until the workload is full
                if count >= self.tiles:
                    # all done
                    return
                # publish the origin
                yield r, c
                # and count it
                count += 1
        # all done
        return

    def _launch(self, reader):
        """
        Launch the installed qed server with the swarm configuration
        """
        # the server output lands next to the measurement records
        stem = os.path.splitext(self.output)[0]
        # open its log
        log = open(f"{stem}-server.log", mode="w")
        # assemble the launch command; the {nexus} node is not an application trait, so its
        # settings must use the fully qualified names
        cmd = [
            # the installed driver
            "qed",
            # serve, without spawning a browser
            "--shell=web",
            "--shell.auto=no",
            # on the swarm port
            f"--qed.app.nexus.services.web.address=ip4:127.0.0.1:{self.port}",
            # with the tile cache off, so every request is an actual render
            "--qed.app.nexus.services.web.fleet.cache.capacity=0",
            # with the requested team size for the target reader
            f"--qed.app.nexus.services.web.fleet.{reader.pyre_name}.size={self.team}",
        ]
        # launch
        process = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
        # hand back the process and its log
        return process, log

    def _ready(self):
        """
        Wait for the launched server to accept connections
        """
        # the probe url
        url = f"http://127.0.0.1:{self.port}/"
        # try for a while
        for _ in range(30):
            # attempt to
            try:
                # touch the server
                with urllib.request.urlopen(url, timeout=2):
                    # any response means it is up
                    return True
            # an http level complaint still means the server is up
            except urllib.error.HTTPError:
                # so we are done waiting
                return True
            # anything at the transport level means it is not up yet
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                # wait a beat
                time.sleep(1)
                # and try again
                continue
        # the server never came up
        return False

    def _select(self, reader, channel):
        """
        Drive the server side view state to the target {reader} and {channel}
        """
        # select the reader in viewport 0
        self._graphql(
            query=(
                f"mutation {{ viewReaderSelect(input: {{viewport: 0, "
                f'reader: "{reader.pyre_name}"}}) {{ view {{ dataset {{ name }} }} }} }}'
            )
        )
        # and pick the channel
        self._graphql(
            query=(
                f"mutation {{ viewChannelSet(input: {{viewport: 0, "
                f'reader: "{reader.pyre_name}", value: "{channel}"}}) '
                f"{{ views {{ channel {{ tag }} }} }} }}"
            )
        )
        # all done
        return

    def _graphql(self, query):
        """
        Post a graphql {query} to the launched server
        """
        # encode the payload
        payload = json.dumps({"query": query}).encode("utf-8")
        # assemble the request
        request = urllib.request.Request(
            url=f"http://127.0.0.1:{self.port}/graphql",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        # post it
        with urllib.request.urlopen(request, timeout=30) as response:
            # and decode the answer
            return json.loads(response.read())

    def _batch(self, urls, workers):
        """
        Fetch all {urls} with {workers} concurrent clients; return the batch wall time in
        ms, the per-request latencies of the successes, and the failure count
        """
        # the successful latencies
        latencies = []
        # and the failure count
        failures = 0
        # read the clock
        start = time.perf_counter()
        # make the client pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            # fetch everything
            for latency in pool.map(self._pull, urls):
                # a missing latency marks a failed request
                if latency is None:
                    # count it
                    failures += 1
                # otherwise
                else:
                    # collect it
                    latencies.append(latency)
        # read the clock again
        elapsed = (time.perf_counter() - start) * 1000
        # all done
        return elapsed, latencies, failures

    def _pull(self, url):
        """
        Fetch one tile and return its latency in ms, or None on failure
        """
        # read the clock
        start = time.perf_counter()
        # attempt to
        try:
            # fetch the tile
            with urllib.request.urlopen(url, timeout=60) as response:
                # and drain the payload
                response.read()
        # a request that failed at any level
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            # yields no latency
            return None
        # report the round trip
        return (time.perf_counter() - start) * 1000

    def _stop(self, process, log):
        """
        Bring the launched server down and close its log
        """
        # attempt to
        try:
            # ask it to shut down
            with urllib.request.urlopen(
                f"http://127.0.0.1:{self.port}/stop", timeout=5
            ):
                # nothing else to do with the response
                pass
        # the server may drop the connection while dying; that's a successful stop
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            # so no complaints
            pass
        # attempt to
        try:
            # wait for it to exit
            process.wait(timeout=10)
        # if it lingers
        except subprocess.TimeoutExpired:
            # put it down
            process.kill()
            # and reap it
            process.wait()
        # close the log
        log.close()
        # all done
        return

    def _tabulate(self, channel, dataset, name, zoom, span, count, results):
        """
        Persist the swarm {results} and report the speedup at each concurrency level
        """
        # the swarm records land next to the tile records
        stem = os.path.splitext(self.output)[0]
        # in their own file
        path = f"{stem}-swarm.csv"
        # check whether this is first contact
        fresh = not os.path.exists(path)
        # open the file for appending, so swarm runs accumulate
        with open(path, mode="a", newline="") as stream:
            # make a writer
            writer = csv.writer(stream)
            # on first contact
            if fresh:
                # write the header
                writer.writerow(self._swarmHeaders)
            # the single client rate anchors the speedup column
            baseline = results[0][2] if results else 0
            # sign on
            channel.line(
                f"swarm: {dataset.pyre_name}.{name}, {count} tiles of "
                f"{span}x{span} @ zoom {zoom}, team of {self.team}:"
            )
            # go through the levels
            for workers, elapsed, rate, latencies, failures in results:
                # order the latencies
                latencies.sort()
                # so the percentiles are direct lookups
                mean = sum(latencies) / len(latencies) if latencies else 0
                median = latencies[len(latencies) // 2] if latencies else 0
                p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
                # the measured speedup over one client
                speedup = rate / baseline if baseline > 0 else 0
                # record the level
                writer.writerow(
                    (
                        self.pyre_host.nickname,
                        dataset.pyre_name,
                        name,
                        zoom,
                        span,
                        count,
                        workers,
                        self.team,
                        f"{elapsed:.1f}",
                        f"{rate:.2f}",
                        f"{mean:.1f}",
                        f"{median:.1f}",
                        f"{p95:.1f}",
                        failures,
                    )
                )
                # and report it
                channel.line(
                    f"  {workers:4} clients: {rate:6.1f} tiles/s, "
                    f"speedup {speedup:4.2f}, median {median:.1f} ms, p95 {p95:.1f} ms"
                )
        # all done
        return

    # private data
    # the column labels of the per-request records
    _tileHeaders = (
        "stage",
        "host",
        "dataset",
        "channel",
        "cell",
        "zoom",
        "span",
        "pixels",
        "cells",
        "cache",
        "trial",
        "wall_ms",
        "cpu_ms",
    )
    # the column labels of the swarm records
    _swarmHeaders = (
        "host",
        "dataset",
        "channel",
        "zoom",
        "span",
        "tiles",
        "clients",
        "team",
        "batch_ms",
        "tiles_per_s",
        "mean_ms",
        "median_ms",
        "p95_ms",
        "failures",
    )


# end of file
