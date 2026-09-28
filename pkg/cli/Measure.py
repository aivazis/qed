# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import collections
import contextlib
import csv
import datetime
import functools
import gzip
import journal
import json
import math
import os
import pyre
import selectors
import shutil
import socket
import statistics
import subprocess
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request

# support
import qed

# the clients of the swarm
from .TileClient import TileClient

# the channel the event loop watches the output of a measurement through
from pyre.ipc.Pipe import Pipe

# the unit of the deadlines
from pyre.units.SI import second

# the NISAR readers the programs that measure products in a bucket know about
FLAVORS = ("rrsd", "rslc", "rifg", "runw", "roff", "gslc", "gunw", "gcov", "goff")


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

    rasters = qed.properties.strings()
    rasters.default = []
    rasters.doc = "restrict the sweep to the datasets with these names; empty sweeps all"

    # sweep geometry
    shapes = qed.properties.tuple(schema=qed.properties.int())
    shapes.default = (8, 12)
    shapes.doc = "the half open range of tile shape exponents; (8,12) sweeps 256 through 2048"

    zooms = qed.properties.tuple(schema=qed.properties.int())
    zooms.default = (0, 3)
    zooms.doc = "the half open range of zoom levels; higher zoom pulls a larger source footprint"

    # not {origin}: panel traits alias globally, and the plexus has an {origin} of its own
    corner = qed.properties.tuple(schema=qed.properties.int())
    corner.default = None
    corner.doc = "the tile origin, in decimated coordinates; unset aims at data near the center"

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

    sample = qed.properties.bool()
    sample.default = True
    sample.doc = "sample the display range at first contact; off keeps it from warming the tiles"

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

    warm = qed.properties.bool()
    warm.default = True
    warm.doc = (
        "warm the workers with a full pass first; off gives every level tiles nobody has fetched"
    )

    rate = qed.properties.float()
    rate.default = 20.0
    rate.doc = "the tiles per second the contention program asks for, the way a panning client does"

    workload = qed.properties.str()
    workload.default = "data"
    workload.validators = qed.constraints.isMember("data", "fill", "cached")
    workload.doc = (
        "what the tiles of the swarm cost: 'data' aims them at data; 'fill' aims them at chunks "
        "that were never written, which the workers answer without reading anything; 'cached' "
        "replays tiles the server keeps in its tile cache, which involves no worker at all"
    )

    levels = qed.properties.bool()
    levels.default = True
    levels.doc = (
        "let the launched server build reduced resolution levels; off reads the product itself"
    )

    # crew configuration
    crews = qed.properties.tuple(schema=qed.properties.int())
    crews.default = (1, 2, 4, 8, 16)
    crews.doc = "the sequence of team sizes to sweep in the whole-dataset pass"

    resolution = qed.properties.int()
    resolution.default = 2048
    resolution.doc = "the target long axis of the decimated whole-dataset pass"

    # the caches of the HDF5 library
    buffers = qed.properties.tuple(schema=qed.properties.int())
    buffers.default = (0, 64, 4096)
    buffers.doc = "the page buffer sizes the cache program sweeps, in MiB; zero means none"

    budgets = qed.properties.tuple(schema=qed.properties.int())
    budgets.default = (0, 64)
    budgets.doc = (
        "the chunk cache sizes the cache program sweeps, in MiB; zero keeps the library default"
    )

    patterns = qed.properties.strings()
    patterns.default = ["stream", "revisit"]
    patterns.validators = qed.constraints.isSubset(choices=["stream", "revisit"])
    patterns.doc = (
        "the access patterns the cache program sweeps: 'stream' reads every chunk of a block "
        "once, in the order of their addresses, the way a build does; 'revisit' reads the "
        "block twice, a chunk at a time in raster order, the way a tile team does"
    )

    block = qed.properties.int()
    block.default = 8
    block.doc = "the side of the block the cache program reads, in chunks"

    location = qed.properties.str()
    location.default = None
    location.doc = (
        "the path of the measured dataset in its file; the cache program sets it for the "
        "processes it launches, so they open the dataset before the reader does"
    )

    # page occupancy
    chunks = qed.properties.bool()
    chunks.default = True
    chunks.doc = "record every chunk of each dataset; off keeps only the per dataset summaries"

    compress = qed.properties.bool()
    compress.default = False
    compress.doc = "compress the records of the chunks with gzip"

    # the s3 program; not {product}, since the program registers its granule under that name,
    # and panel traits alias globally
    granule = qed.properties.str()
    granule.default = None
    granule.doc = "the s3 uri of the NISAR granule the s3 program measures"

    flavor = qed.properties.str()
    flavor.default = "gslc"
    flavor.validators = qed.constraints.isMember(*FLAVORS)
    flavor.doc = "the NISAR reader that understands the granule of the s3 program"

    depth = qed.properties.int()
    depth.default = 6
    depth.doc = "the deepest zoom level of the s3 zoom ladder; 6 is the deepest the client asks for"

    results = qed.properties.path()
    results.default = None
    results.doc = (
        "the directory that collects the results of the s3 program, unset names one after the "
        "host and the time; for a census, the directory that holds a folder for each product, "
        "named after the cycle and the product, e.g. census-31-rslc, unset is the current one"
    )

    # the census of the layout of the NISAR products in a bucket
    bucket = qed.properties.str()
    bucket.default = "s3://nisar-ops-rs-fwd/products/"
    bucket.doc = (
        "the prefix under which the census finds the NISAR products, in the canonical layout of "
        "product, date, and granule"
    )

    quota = qed.properties.int()
    quota.default = None
    quota.doc = (
        "the number of granules of each product the census measures, spread evenly over the "
        "cycle; unset measures every one"
    )

    scrape = qed.properties.path()
    scrape.default = None
    scrape.doc = (
        "a scrape of the bucket, a folder with a list of granule ids for each product named "
        "after its reader, e.g. rslc.txt, that the census takes its granules from"
    )

    check = qed.properties.int()
    check.default = None
    check.doc = (
        "the number of granules of each product in each complete cycle the cycles report looks up "
        "in the bucket; unset looks up none"
    )

    inputs = qed.properties.strings()
    inputs.default = []
    inputs.doc = (
        "the censuses to digest or compare, as the folders or the tarballs they left behind"
    )

    cycle = qed.properties.int()
    cycle.default = None
    cycle.doc = "the repeat cycle whose granules the census takes from the scrape"

    workers = qed.properties.int()
    workers.default = 8
    workers.doc = "the number of granules the census measures at the same time"

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
        parallel ceiling through Amdahl's law, and the swarm measures the actual speedup. The
        {workload} decides what the tiles cost: tiles that cost nothing, served from the tile
        cache or made of fill, measure the ceiling of the server itself, and a swarm of tiles of
        data that reaches the same ceiling is limited by the server rather than by the data
        """
        # make a channel
        channel = journal.info("qed.measure.swarm")
        # pick the first target the restrictions allow
        first = next(self._targets(plexus=plexus), None)
        # if there is none
        if first is None:
            # complain
            error = journal.error("qed.measure.swarm")
            error.log("no dataset to measure; check the configuration and the restrictions")
            # and bail
            return 1
        # unpack the target
        reader, dataset, name, _ = first
        # the workload geometry: the smallest configured tile at the lowest configured zoom
        span = 2 ** self.shapes[0]
        zoom = self.zooms[0]
        # tiles served from the cache have to be put there first, by a warm up pass
        warm = self.warm or self.workload == "cached"
        # a warm swarm replays one workload at every level; a cold one needs a workload for
        # each level, so that no level is served tiles an earlier one already fetched
        batches = 1 if warm else len(self.clients)
        # the tiles of fill
        if self.workload == "fill":
            # lie where no chunk was written
            origins = list(
                self._void(dataset=dataset, span=span, zoom=zoom, count=self.tiles * batches)
            )
        # all others
        else:
            # lay out the workload as a grid of distinct tiles; identical in-flight requests
            # collapse in the team workplan, so distinct tiles are essential to load the workers
            origins = list(
                self._grid(dataset=dataset, span=span, zoom=zoom, count=self.tiles * batches)
            )
        # if the raster cannot hold even one tile per batch
        if len(origins) < batches:
            # complain
            error = journal.error("qed.measure.swarm")
            error.log(f"'{dataset.pyre_name}' cannot fit a {span}x{span} tile at zoom {zoom}")
            # and bail
            return 1
        # if the raster ran out of room before the workload filled up
        if len(origins) < self.tiles * batches:
            # say so, so a smaller workload is never mistaken for the requested one
            channel.line(f"workload truncated to {len(origins)} of {self.tiles * batches} tiles")
        # the share of each batch
        share = len(origins) // batches
        # assemble the tile request urls, one list per batch
        workloads = [
            [
                f"http://127.0.0.1:{self.port}"
                f"/data/0/{dataset.pyre_name}/{name}/{zoom}x{zoom}/{r}x{c}+{span}x{span}"
                for r, c in origins[batch * share : (batch + 1) * share]
            ]
            for batch in range(batches)
        ]
        # launch the server, with its tile cache on only when the workload is served from it
        process, log = self._launch(reader=reader, cache=self.workload == "cached")
        # from here on, the server must come down no matter what happens
        try:
            # wait for it to accept connections
            if not self._ready():
                # if it never came up, complain
                error = journal.error("qed.measure.swarm")
                error.log(f"the server on port {self.port} never came up; see '{log.name}'")
                # and bail
                return 1
            # the tile path resolves its reader through server side view state, so drive the
            # selections the way the client would
            self._select(reader=reader, dataset=dataset, channel=name)
            # a warm swarm
            if warm:
                # warms up with one full pass so every concurrency level sees the same caches
                self._batch(urls=workloads[0], workers=max(self.clients))
            # the collected results, one entry per concurrency level
            results = []
            # sweep the concurrency levels
            for level, workers in enumerate(self.clients):
                # fire the workload of this level
                elapsed, latencies, failures = self._batch(
                    urls=workloads[level % batches], workers=workers
                )
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
                channel.line(f"{workers:4} clients: {rate:6.1f} tiles/s, batch {elapsed:.0f} ms")
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
            count=share,
            results=results,
        )
        # flush the report
        channel.log()
        # all done
        return 0

    @qed.export(tip="measure the whole-dataset pass as a function of crew size")
    def crew(self, plexus, **kwds):
        """
        Replay the whole-dataset pass against servers of increasing team size and record
        the wall time of each

        The pass is the one the minimap thumbnail already performs: decimate the raster
        until its long axis is a few thousand pixels, chop the result into chunk-aligned
        slices, and render them all. It is the only workload that touches every chunk of a
        product, which makes it both the natural seed for whole-dataset statistics and the
        thing worth knowing the parallel cost of
        """
        # make a channel
        channel = journal.info("qed.measure.crew")
        # pick the first target the restrictions allow
        first = next(self._targets(plexus=plexus), None)
        # if there is none
        if first is None:
            # complain
            error = journal.error("qed.measure.crew")
            error.log("no dataset to measure; check the configuration and the restrictions")
            # and bail
            return 1
        # unpack the target
        reader, dataset, name, _ = first
        # lay out the pass
        exp, slices = self._thumbnail(dataset=dataset)
        # if the raster cannot be decomposed
        if not slices:
            # complain
            error = journal.error("qed.measure.crew")
            error.log(f"'{dataset.pyre_name}' yielded no slices")
            # and bail
            return 1
        # report the geometry, so the numbers below can be read against it
        channel.line(
            f"{dataset.pyre_name}: {len(slices)} slices at zoom {exp}, "
            f"stride {2**exp}, tile {tuple(dataset.tile)}"
        )
        # assemble the request urls
        urls = [
            f"http://127.0.0.1:{self.port}"
            f"/data/0/{dataset.pyre_name}/{name}/{exp}x{exp}/{r}x{c}+{h}x{w}"
            for r, c, h, w in slices
        ]
        # the collected results, one entry per team size
        results = []
        # the intrinsic cost of each slice, measured once, serially
        costs = None
        # sweep the team sizes
        for size in self.crews:
            # the launcher reads the team size off me, so install this one
            self.team = size
            # launch a server that renders with a team of this size
            process, log = self._launch(reader=reader)
            # from here on, the server must come down no matter what happens
            try:
                # wait for it to accept connections
                if not self._ready():
                    # if it never came up, complain
                    error = journal.error("qed.measure.crew")
                    error.log(f"the server on port {self.port} never came up; see '{log.name}'")
                    # and bail
                    return 1
                # the tile path resolves its reader through server side view state, so
                # drive the selections the way the client would
                self._select(reader=reader, dataset=dataset, channel=name)
                # on the first level, walk the slices one at a time: under concurrency a
                # request waits behind its peers, so its latency measures queueing rather
                # than work, and the intrinsic cost of a slice shows only serially
                if costs is None:
                    # pay for one serial pass; the load balance is read from it
                    _, costs, _ = self._batch(urls=urls, workers=1)
                # fire the whole pass at once, the way the thumbnail does; every slice is
                # distinct, so nothing collapses in the workplan
                elapsed, latencies, failures = self._batch(urls=urls, workers=len(urls))
            # no matter how the pass went
            finally:
                # bring the server down
                self._stop(process=process, log=log)
            # failed requests void the level; say so rather than reporting on the rest
            if failures:
                # complain
                warning = journal.warning("qed.measure.crew")
                warning.log(f"{failures} slices failed with a team of {size}")
            # collect the level
            results.append((size, elapsed, latencies))
            # show me
            channel.line(f"team {size:3}: {elapsed / 1000:7.2f} s")
        # the smallest team sets the reference the speedups are measured against
        _, base, _ = results[0]
        # report the shape of the curve
        channel.line("")
        channel.line("speedup against the smallest team:")
        # go through the levels
        for size, elapsed, _ in results:
            # the speedup this team achieved
            speedup = base / elapsed if elapsed else 0
            # show me
            channel.line(f"  team {size:3}: {speedup:5.2f}x")
        # if the serial calibration produced anything
        if costs:
            # the work is only as divisible as its largest indivisible piece: a slice is
            # the unit of work, so no crew can finish the pass faster than its slowest one
            total = sum(costs)
            slowest = max(costs)
            # which sets a ceiling on the speedup, whatever the crew size
            channel.line("")
            channel.line(
                f"load balance: {len(costs)} slices, "
                f"{total / 1000:.2f} s of work in total, "
                f"slowest {slowest / 1000:.2f} s"
            )
            # count the slices that carry the bulk of it
            heavy = [cost for cost in costs if cost > total / len(costs)]
            # and say how concentrated the work is
            channel.line(
                f"  {len(heavy)} of {len(costs)} slices carry "
                f"{sum(heavy) / total * 100:.0f}% of the work, "
                f"so no crew beats {total / slowest:.2f}x"
            )
        # flush the report
        channel.log()
        # all done
        return 0

    @qed.export(tip="measure the construction of the pyramid of a dataset against team size")
    def pyramid(self, plexus, **kwds):
        """
        Build the pyramid of the first dataset the restrictions allow, and of the rasters it is
        read with, on a crew of each of my {crews} sizes, from scratch every time, and record
        how long it takes until the view is worth looking at and until every level is built

        The build is the one the server runs when a client selects the dataset: the same
        layout of the levels, the same decimation tasks, the same crew. Each build works out
        of a folder of its own next to the measurement records, so none finds the levels of
        another; once their size is on record the levels are removed, since a sweep would
        otherwise keep several copies of a pyramid that can be as large as the product
        """
        # make a channel
        channel = journal.info("qed.measure.pyramid")
        # the crews are forked by a clean helper, as the server's are; start it before anything
        # here opens a product: the members must not be copies of a process that has opened one
        qed.nexus.forkserver.start()
        # pick the first target the restrictions allow
        first = next(self._targets(plexus=plexus), None)
        # if there is none
        if first is None:
            # complain
            error = journal.error("qed.measure.pyramid")
            error.log("no dataset to measure; check the configuration and the restrictions")
            # and bail
            return 1
        # unpack the target
        reader, dataset, name, _ = first
        # the records land next to the others
        stem = os.path.splitext(self.output)[0]
        # the host label that lets records from different machines share a file
        host = self.pyre_host.nickname
        # go through the team sizes
        for team in self.crews:
            # the folder of this build
            directory = qed.primitives.path(f"{stem}-pyramid-team{team}").resolve()
            # a folder that exists already may hold the levels of an earlier build
            if directory.exists():
                # which would make this one a measurement of nothing, so refuse it
                error = journal.error("qed.measure.pyramid")
                error.log(f"'{directory}' already exists; its levels would be reused")
                # and bail
                return 1
            # make it
            directory.mkdir(parents=True)
            # build the pyramid and time it
            seeded, ready, status = self._build(
                reader=reader, dataset=dataset, team=team, directory=directory
            )
            # the bytes the levels occupy on disk; the levels are sized before any tile is
            # written, so the files are sparse and only the blocks that were written count
            size = sum(
                os.stat(os.path.join(root, entry)).st_blocks * 512
                for root, _, entries in os.walk(str(directory))
                for entry in entries
            )
            # the levels have served their purpose
            shutil.rmtree(str(directory))
            # record the build
            with self._records(path=f"{stem}-pyramid.csv", headers=self._pyramidHeaders) as out:
                # in one row
                out.writerow((host, dataset.pyre_name, name, team, seeded, ready, status, size))
            # and report it
            channel.line(
                f"team of {team}: {status}; seeded after "
                + (f"{seeded:.1f} s" if seeded is not None else "never")
                + ", ready after "
                + (f"{ready:.1f} s" if ready is not None else "never")
                + f"; {size / 2**20:.0f} MiB of levels"
            )
        # flush the report
        channel.log()
        # all done
        return 0

    @qed.export(
        tip="measure the latency of tiles while the team builds the pyramid of their dataset"
    )
    def contention(self, plexus, **kwds):
        """
        Keep a few tiles of the first dataset the restrictions allow in flight on its team
        while the team builds the pyramid of the dataset, and again once the build is over, and
        record the latency of every tile

        The build and the tiles run in this process, on a crew of {team}, the way the server
        runs them, so what is measured is how long a tile waits behind the build in the
        workplan of the team; the path of a request through the server is left out, since the
        swarm measures it on its own. Tiles are asked for at a steady {rate}, for as long as the
        build runs, and then {tiles} more at the same rate; the first of {shapes} and {zooms}
        are their size and zoom
        """
        # make a channel
        channel = journal.info("qed.measure.contention")
        # pick the first target the restrictions allow
        first = next(self._targets(plexus=plexus), None)
        # if there is none
        if first is None:
            # complain
            error = journal.error("qed.measure.contention")
            error.log("no dataset to measure; check the configuration and the restrictions")
            # and bail
            return 1
        # unpack the target
        reader, dataset, name, _ = first
        # a tile task is described by a view, so point one at the target
        view = self._view(plexus=plexus, reader=reader, dataset=dataset, channel=name)
        # if the view did not land on it
        if view is None:
            # complain
            error = journal.error("qed.measure.contention")
            error.log(f"could not point a view at '{dataset.pyre_name}.{name}'")
            # and bail
            return 1
        # the records land next to the others
        stem = os.path.splitext(self.output)[0]
        # the folder the levels of this build go into
        directory = qed.primitives.path(f"{stem}-contention-team{self.team}").resolve()
        # a folder that exists already may hold the levels of an earlier build
        if directory.exists():
            # which would make this one a measurement of nothing, so refuse it
            error = journal.error("qed.measure.contention")
            error.log(f"'{directory}' already exists; its levels would be reused")
            # and bail
            return 1
        # make it
        directory.mkdir(parents=True)
        # the levels must go, whatever happens
        try:
            # run the tiles against the build
            seeded, ready, status, records = self._contend(
                reader=reader, dataset=dataset, name=name, view=view, directory=directory
            )
        # no matter how it went
        finally:
            # the levels have served their purpose
            shutil.rmtree(str(directory))
        # the host label that lets records from different machines share a file
        host = self.pyre_host.nickname
        # the shape of the tiles
        span = 2 ** self.shapes[0]
        # record every tile
        with self._records(path=f"{stem}-contention.csv", headers=self._contentionHeaders) as out:
            # one row each
            for phase, submitted, latency, failure in records:
                # with everything that distinguishes the run
                out.writerow(
                    (
                        host,
                        dataset.pyre_name,
                        name,
                        self.team,
                        self.rate,
                        self.zooms[0],
                        span,
                        phase,
                        f"{submitted:.3f}",
                        f"{latency:.1f}",
                        "failed" if failure else "ok",
                        f"{seeded:.3f}" if seeded is not None else "",
                        f"{ready:.3f}" if ready is not None else "",
                    )
                )
        # report the build
        channel.line(
            f"{dataset.pyre_name}.{name}, team of {self.team}, {self.rate:g} tiles of "
            f"{span}x{span} @ zoom {self.zooms[0]} per second: build {status}, seeded after "
            + (f"{seeded:.1f} s" if seeded is not None else "never")
            + ", ready after "
            + (f"{ready:.1f} s" if ready is not None else "never")
        )
        # and the latencies of each phase
        for phase in ("build", "after"):
            # the tiles of this phase that were delivered
            latencies = sorted(
                latency for kind, _, latency, failure in records if kind == phase and not failure
            )
            # the ones that were not
            failures = sum(1 for kind, _, _, failure in records if kind == phase and failure)
            # a phase without tiles
            if not latencies:
                # says so
                channel.line(f"  {phase:5}: no tiles, {failures} failed")
                # and moves on
                continue
            # the summary of the rest
            channel.line(
                f"  {phase:5}: {len(latencies)} tiles, "
                f"median {latencies[len(latencies) // 2]:.1f} ms, "
                f"p95 {latencies[int(len(latencies) * 0.95)]:.1f} ms, "
                f"max {latencies[-1]:.1f} ms, {failures} failed"
            )
        # flush the report
        channel.log()
        # all done
        return 0

    @qed.export(tip="measure the page buffer and the chunk cache in the access patterns of crews")
    def caches(self, plexus, **kwds):
        """
        Read a block of chunks that hold data from the first dataset the restrictions allow,
        in each access pattern, with each page buffer size and chunk cache size, and record the
        resident memory, the activity of the page buffer, and the time of every pass

        Every configuration runs in a fresh process, so that neither the caches nor the memory
        of one configuration carry over to the next. The process opens the dataset before the
        reader does: a second open of a file, or of a dataset, in the same process shares the
        caches of the first, whatever its access lists ask for
        """
        # make a channel for the problems that stop the program before it starts
        error = journal.error("qed.measure.caches")
        # a process launched by a sweep knows where its dataset is
        if self.location is not None:
            # so it measures its one configuration and reports its status
            return self._cacheRun(
                plexus=plexus,
                pattern=self.patterns[0],
                buffer=self.buffers[0],
                budget=self.budgets[0],
            )
        # otherwise, pick the first raster the restrictions allow
        first = next(self._rasters(plexus=plexus), None)
        # if there is none
        if first is None:
            # complain
            error.log("no dataset to measure; check the configuration and the restrictions")
            # and bail
            return 1
        # unpack it
        reader, dataset = first
        # a reader that is not an HDF5 product
        if not isinstance(reader, qed.readers.nisar.h5):
            # has no caches to measure
            error.log(f"'{reader.pyre_name}' is not an HDF5 product")
            # so bail
            return 1
        # the configurations to measure
        configurations = [
            (pattern, buffer, budget)
            for pattern in self.patterns
            for buffer in self.buffers
            for budget in self.budgets
        ]
        # make a channel for the progress report
        channel = journal.info("qed.measure.caches")
        # go through the configurations
        for pattern, buffer, budget in configurations:
            # narrow the sweep to this one and hand it to a fresh process
            cmd = [
                "qed",
                "measure",
                "caches",
                # the configuration may prefer the web shell; the child is a CLI run
                "--shell=script",
                f"--only={reader.pyre_name}",
                f"--rasters={dataset.pyre_name}",
                f"--patterns={pattern}",
                f"--buffers={buffer}",
                f"--budgets={budget}",
                f"--block={self.block}",
                f"--location={dataset.data._dataset._pyre_location}",
                f"--output={self.output}",
            ]
            # show me
            channel.log(
                f"{dataset.pyre_name}: {pattern}, page buffer {buffer} MiB, "
                f"chunk cache {budget or 'default'} MiB"
            )
            # launch and wait
            got = subprocess.run(cmd)
            # if the configuration failed
            if got.returncode != 0:
                # a missing record is easy to miss, so make it loud
                warning = journal.warning("qed.measure.caches")
                warning.log(f"{pattern}, {buffer} MiB, {budget} MiB: failed")
        # all done
        return 0

    @qed.export(tip="measure how the chunks of each dataset occupy the pages of its file")
    def pages(self, plexus, **kwds):
        """
        Walk the chunk table of each dataset and report how its chunks sit on the pages of
        the file: how many pages a chunk spans, how full those pages are, and how many bytes
        a reader that fetches whole pages, e.g. {ros3}, moves for every byte it needs

        Only metadata is read, so this is cheap even for a product in a bucket
        """
        # make a channel
        channel = journal.info("qed.measure.pages")
        # the host label that lets records from different machines share a file
        host = self.pyre_host.nickname
        # the records land next to the others
        stem = os.path.splitext(self.output)[0]
        # the datasets the restrictions allow, grouped by the reader whose file holds them
        readers = {}
        # attempt to
        try:
            # go through them
            for reader, dataset in self._rasters(plexus=plexus):
                # and file each one with its reader
                readers.setdefault(reader, []).append(dataset)
        # if a product could not be opened
        except qed.h5.api.exceptions.OpenError as error:
            # and that is because it is not there
            if self._missing(uri=error.uri):
                # say so
                channel.log(f"there is no product at '{error.uri}'")
                # and report it with the status that says so
                return self._absent
            # anything else is a failure, and says why
            raise
        # open the file of per chunk records and the file of per dataset summaries, for
        # appending, so runs accumulate
        with (
            self._records(
                path=(f"{stem}-pages.csv{'.gz' if self.compress else ''}" if self.chunks else None),
                headers=self._pageHeaders,
            ) as chunks,
            self._records(path=f"{stem}-occupancy.csv", headers=self._occupancyHeaders) as sums,
        ):
            # go through the readers
            for reader, datasets in readers.items():
                # the file layout is shared by all the datasets of a reader
                layout = qed.readers.pages.paging(reader=reader)
                # a reader whose file is not HDF5 has no pages to speak of
                if layout is None:
                    # so say so
                    channel.line(f"{reader.pyre_name}: not an HDF5 product")
                    # and move on
                    continue
                # the chunk tables of every dataset in the file, since the datasets that share
                # the pages of the one being measured decide how much of each page it needs
                tables = qed.readers.pages.tables(reader=reader)
                # go through the datasets to measure
                for dataset in datasets:
                    # and measure each one
                    self._occupancy(
                        channel=channel,
                        chunks=chunks,
                        summaries=sums,
                        host=host,
                        reader=reader,
                        dataset=dataset,
                        layout=layout,
                        tables=tables,
                    )
        # flush the report
        channel.log()
        # all done
        return 0

    @qed.export(tip="measure tile generation from a NISAR granule in an S3 bucket")
    def s3(self, plexus, **kwds):
        """
        Measure tile generation from the NISAR {granule} in an S3 bucket: the page layout of
        the file, the cost of a tile at every zoom level the client requests, the cost of each
        tile size, the fit of the cost model, and the throughput of a server as a function of
        its team size, with everything collected in a fresh {results} directory that is packed
        into a tarball at the end

        Each measurement runs in a fresh process, so no cache carries over from one to the
        next. The run takes a while, so start it under nohup or inside tmux
        """
        # make a channel for the problems that stop the program before it starts
        error = journal.error("qed.measure.s3")
        # a granule is required
        if self.granule is None:
            # so complain
            error.log("no granule to measure; point {granule} at its s3 uri")
            # and bail
            return 1
        # and it has to be in a bucket
        if not self.granule.startswith("s3://"):
            # or else this is the wrong program
            error.log(f"'{self.granule}' is not an s3 uri")
            # so bail
            return 1
        # the measurements run in child processes of the installed qed
        if shutil.which("qed") is None:
            # so it must be on the path
            error.log("there is no 'qed' on the path to run the measurements")
            # or there is nothing to measure with
            return 1
        # the swarms launch servers on my port
        if not self._s3port():
            # which somebody else holds
            error.log(f"port {self.port} is taken; pick another with {{port}}")
            # so bail
            return 1
        # the reader, read here so its validator runs before anything is spent
        flavor = self.flavor
        # the directory that collects the results
        results = self._results()
        # a directory that exists already would mix records from different runs
        if results.exists():
            # so refuse it
            error.log(f"'{results}' already exists")
            # and bail
            return 1
        # make it
        results.mkdir(parents=True)

        # make a channel for the progress of the program
        channel = journal.info("qed.measure.s3")
        # which reaches the console and the run log alike
        channel.device = journal.tee(paths=[str(results / "run.log")])
        # the number of cores, which caps the team sizes
        cores = os.cpu_count()
        # the team sizes the machine can staff
        teams = [size for size in self.crews if size <= cores]
        # say what is about to happen
        channel.line(f"on {self.pyre_host.nickname}, {cores} cores")
        channel.line(f"granule {self.granule} as nisar.{flavor}")
        channel.line(f"results in {results}")
        # flush
        channel.log()

        # record the installation, so the numbers can be tied to the code that produced them
        self._about(channel=channel, results=results)
        # write the configuration every measurement reads
        self._configure(directory=results, uri=self.granule, flavor=flavor)
        # find out what the granule holds, which also checks that it can be reached at all
        datasets = self._s3survey()
        # keep the description of the granule
        with open(results / "product.txt", mode="w") as stream:
            # one dataset per line
            for name, shape, tile, channels in datasets:
                # with its shape, its tile, and its channels
                stream.write(
                    f"{name} {shape[0]}x{shape[1]} {tile[0]}x{tile[1]} {','.join(channels)}\n"
                )
                # and show it
                channel.line(
                    f"{name} {shape[0]}x{shape[1]} {tile[0]}x{tile[1]} {','.join(channels)}"
                )
        # flush
        channel.log()
        # choose what to measure
        target = self._s3pick(datasets=datasets)
        # if the granule lacks what was asked for
        if target is None:
            # the reason has been reported; pack what there is, so the record is complete
            self._pack(channel=channel, results=results)
            # and bail
            return 1
        # unpack the choice
        dataset, name = target
        # say what will be measured
        channel.log(f"measuring {dataset}, channel {name}")

        # the restrictions every measurement shares
        restrictions = ["--only=product", f"--rasters={dataset}", f"--channels={name}"]
        # the measurements that did not complete
        failures = []

        # the layout of the chunks on the pages of the file, which says how many bytes the
        # driver fetches for every byte a tile needs; it reads nothing but metadata
        self._s3run(
            channel=channel,
            results=results,
            label="page occupancy",
            args=["pages", "--only=product", f"--output={results / 'layout.csv'}"],
            failures=failures,
        )
        # the zoom levels: a 512 tile, the one the client asks for, at every decimation the
        # client requests, each point in a fresh process so nothing is served from a cache
        for trial in range(1, self.trials + 1):
            # measure
            self._s3run(
                channel=channel,
                results=results,
                label=f"zoom ladder, pass {trial} of {self.trials}",
                args=[
                    "tile",
                    *restrictions,
                    "--shapes=9,10",
                    f"--zooms=0,{self.depth + 1}",
                    "--cold=yes",
                    "--sample=no",
                    f"--output={results / 'tiles.csv'}",
                ],
                failures=failures,
            )
        # the tile sizes: 256 through 2048 at full resolution, which separates the fixed cost
        # of a request from the cost of each pixel
        for trial in range(1, self.trials + 1):
            # measure
            self._s3run(
                channel=channel,
                results=results,
                label=f"shape ladder, pass {trial} of {self.trials}",
                args=[
                    "tile",
                    *restrictions,
                    "--shapes=8,12",
                    "--zooms=0,1",
                    "--cold=yes",
                    "--sample=no",
                    f"--output={results / 'tiles.csv'}",
                ],
                failures=failures,
            )
        # fit the cost model to everything the ladders recorded
        self._s3run(
            channel=channel,
            results=results,
            label="fit",
            args=["fit", f"--output={results / 'tiles.csv'}"],
            failures=failures,
        )
        # the team sizes: a server per size, full resolution tiles of 512, every concurrency
        # level served tiles nobody has fetched, and no pyramid, so every tile is read from the
        # bucket
        for team in teams:
            # measure
            self._s3run(
                channel=channel,
                results=results,
                label=f"swarm with a team of {team}",
                args=[
                    "swarm",
                    *restrictions,
                    "--shapes=9,10",
                    "--zooms=0,1",
                    f"--team={team}",
                    f"--clients={','.join(map(str, self.clients))}",
                    f"--tiles={self.tiles}",
                    "--warm=no",
                    "--levels=no",
                    "--sample=no",
                    f"--port={self.port}",
                    f"--output={results / f'swarm-team{team}.csv'}",
                ],
                failures=failures,
            )

        # the pyramid: built from scratch by a server of each team size, which reads every
        # chunk of the dataset from the bucket once
        self._s3run(
            channel=channel,
            results=results,
            label="pyramid construction",
            args=[
                "pyramid",
                *restrictions,
                f"--crews={','.join(map(str, teams))}",
                "--sample=no",
                f"--port={self.port}",
                f"--output={results / 'build.csv'}",
            ],
            failures=failures,
        )

        # say it is over
        channel.line("done")
        # and list whatever did not complete, so a partial result is never mistaken for a whole
        for label in failures:
            # one per line
            channel.line(f"incomplete: {label}")
        # flush
        channel.log()
        # pack the results
        self._pack(channel=channel, results=results)
        # report failures through the exit status too
        return 1 if failures else 0

    @qed.export(tip="measure the page layout of a sample of the NISAR products in a bucket")
    def census(self, plexus, **kwds):
        """
        Measure the page layout of the granules of one repeat {cycle} in a {scrape} of {bucket},
        all of them or {quota} of each product, for the products my {only} restriction names, or
        for every list in the scrape that qed has a reader for, and collect the summaries of every
        dataset in one table, so the structure of the products can be compared across products
        and processing versions

        Each granule is measured by {measure pages} in a fresh process, {workers} at a time;
        only metadata is read, so the census is cheap next to the data
        """
        # make a channel for the problems that stop the census before it starts
        error = journal.error("qed.measure.census")
        # the granules come from a scrape
        if self.scrape is None:
            # so a census without one is a mistake
            error.log("the census takes its granules from a scrape; point {scrape} at one")
            # and bail
            return 1
        # whose lists are named after their products
        lists = sorted(
            name.removesuffix(".txt")
            for name in os.listdir(str(self.scrape))
            if name.endswith(".txt")
        )
        # the products to measure: the ones named, or every list qed has a reader for
        products = list(self.only) or [name for name in lists if name in FLAVORS]
        # and the lists left out, when nothing was named
        ignored = [] if self.only else [name for name in lists if name not in FLAVORS]
        # a product without a reader is a mistake
        unknown = [product for product in products if product not in FLAVORS]
        # so say which
        if unknown:
            # and what there is
            error.log(f"no reader for {', '.join(unknown)}; the readers are {', '.join(FLAVORS)}")
            # and bail
            return 1
        # so is one the scrape has no list for
        unlisted = [product for product in products if product not in lists]
        # so say which
        if unlisted:
            # and where the lists are
            error.log(f"the scrape '{self.scrape}' has no list for {', '.join(unlisted)}")
            # and bail
            return 1
        # and a scrape with nothing to measure
        if not products:
            # is a mistake too
            error.log(f"the scrape '{self.scrape}' has no list of a product qed can read")
            # so bail
            return 1
        # which is read one cycle at a time
        if self.cycle is None:
            # so a scrape without a cycle is a mistake
            error.log("the census reads one cycle of a scrape; name it with {cycle}")
            # and bail
            return 1
        # the bucket has to be a bucket
        if not self.bucket.startswith("s3://"):
            # or else this is the wrong program
            error.log(f"'{self.bucket}' is not an s3 uri")
            # so bail
            return 1
        # the measurements tell a missing product from a failure by asking the bucket through the
        # AWS client, which qed does not require
        try:
            # so look for it
            import boto3
        # if it is not there
        except ImportError:
            # say so
            error.log("the census asks the bucket with 'boto3', which is not installed")
            # and bail
            return 1
        # the measurements run in child processes of the installed qed
        if shutil.which("qed") is None:
            # so it must be on the path
            error.log("there is no 'qed' on the path to run the measurements")
            # or there is nothing to measure with
            return 1
        # the folder that holds the folders of the products: my {results}, or the current one
        parent = self.results.resolve() if self.results is not None else qed.primitives.path.cwd()
        # the folder of each product
        folders = {product: parent / f"census-{self.cycle}-{product}" for product in products}
        # a folder that exists already would mix records from different runs; check them all
        # before any of the work starts
        taken = [str(folder) for folder in folders.values() if folder.exists()]
        # so refuse them
        if taken:
            # say which
            error.log(f"already there: {', '.join(taken)}")
            # and bail
            return 1
        # the products whose census did not complete
        incomplete = []
        # go through the products, one after the other
        for product in products:
            # take the census of each one in its own folder
            if self._tour(
                product=product,
                results=folders[product],
                ignored=ignored if product is products[0] else [],
            ):
                # and note the ones that did not complete
                incomplete.append(product)
        # report failures through the exit status too
        return 1 if incomplete else 0

    def _tour(self, product, results, ignored):
        """
        Take the census of one {product} in the {results} folder, and report the {ignored}
        lists of the scrape; hand back whether anything failed
        """
        # make the folder
        results.mkdir(parents=True)
        # the clock of the whole census of this product
        total = qed.timers.wall(f"qed.measure.census.total.{product}")
        # started afresh
        total.reset()
        total.start()
        # make a channel for the progress of the census
        channel = journal.info("qed.measure.census")
        # which reaches the console and the run log of this product alike
        channel.device = journal.tee(paths=[str(results / "run.log")])
        # say what is about to happen
        channel.line(f"on {self.pyre_host.nickname}")
        channel.line(
            f"{'every' if self.quota is None else self.quota} granule(s) of {product}, "
            f"cycle {self.cycle} of the scrape {self.scrape}"
        )
        channel.line(f"from {self.bucket}")
        # the lists of the scrape left out, so nothing goes missing silently
        if ignored:
            # say which
            channel.line(f"lists without a reader, left out: {', '.join(ignored)}")
        channel.line(f"results in {results}")
        # flush
        channel.log()
        # record the installation, so the numbers can be tied to the code that produced them
        self._about(channel=channel, results=results)

        # split the bucket from the prefix
        bucket, _, prefix = self.bucket.removeprefix("s3://").partition("/")
        # choose the granules
        chosen = self._scraped(channel=channel, prefix=prefix, product=product)
        # the granules to measure, as (product, granule, key)
        jobs = [(product, granule, key) for granule, key in chosen]

        # the clock of the measurements
        clock = qed.timers.wall(f"qed.measure.census.measure.{product}")
        # started afresh
        clock.reset()
        clock.start()
        # measure the granules, a few at a time, on the pyre event loop
        failures, absent = self._survey(channel=channel, results=results, bucket=bucket, jobs=jobs)
        # stop the clock
        clock.stop()
        # and report the measurements
        channel.log(
            f"measured {len(jobs) - len(failures) - len(absent)} of {len(jobs)} granules in "
            f"{clock.sec():.1f} s, {self.workers} at a time; {len(absent)} had no product, "
            f"{len(failures)} failed"
        )

        # gather the summaries into one table
        rows = self._gather(results=results, jobs=jobs)
        # and report them
        self._tally(channel=channel, rows=rows)
        # list whatever did not complete, so a partial census is never mistaken for a whole
        for label in failures:
            # one per line
            channel.line(f"incomplete: {label}")
        # stop the clock of the whole census
        total.stop()
        # say it is over
        channel.line(
            f"done: {len(jobs) - len(failures) - len(absent)} of {len(jobs)} granules measured, "
            f"in {total.sec():.1f} s in all"
        )
        # flush
        channel.log()
        # pack the results
        self._pack(channel=channel, results=results)
        # hand back whether anything failed
        return bool(failures)

    @qed.export(tip="count the granules of each product in a scrape by repeat cycle")
    def cycles(self, plexus, **kwds):
        """
        Count the granules of every product my {scrape} has a list for by repeat cycle, mark the
        cycles every product has, and, when asked to {check}, look up that many granules of each
        product in each of those cycles in {bucket}, to see how many still hold their product
        """
        # make a channel for the problems that stop the report before it starts
        error = journal.error("qed.measure.cycles")
        # the counts come from a scrape
        if self.scrape is None:
            # so a report without one is a mistake
            error.log("the report counts the granules of a scrape; point {scrape} at one")
            # and bail
            return 1
        # make a channel for the report
        channel = journal.info("qed.measure.cycles")
        # the products: the ones named, or every list of the scrape
        products = list(self.only) or qed.measurements.scrape.lists(scrape=str(self.scrape))
        # count their granules by cycle
        counts = qed.measurements.scrape.cycles(scrape=str(self.scrape), products=products)
        # the cycles every product has
        complete = qed.measurements.scrape.complete(counts=counts)
        # the cycles any product has
        every = sorted({cycle for tally in counts.values() for cycle in tally if cycle is not None})
        # the report
        lines = [f"# The granules of the scrape {self.scrape}, by repeat cycle", ""]
        # the table of counts
        lines += qed.measurements.census.markdown(
            headers=("cycle", *products, "every product"),
            rows=[
                (cycle, *(counts[product][cycle] for product in products), cycle in complete)
                for cycle in every
            ]
            + [("not recognized", *(counts[product][None] for product in products), "")],
        )
        # if asked to check the bucket
        if self.check is not None and complete:
            # make room
            lines += ["", f"## Products in {self.bucket}, of {self.check} checked", ""]
            # and add the table of what is there
            lines += qed.measurements.census.markdown(
                headers=("cycle", *products),
                rows=[
                    (cycle, *(self._present(product=product, cycle=cycle) for product in products))
                    for cycle in complete
                ],
            )
        # report
        self._publish(
            channel=channel, lines=lines, path=f"cycles-{os.path.basename(str(self.scrape))}.md"
        )
        # all done
        return 0

    @qed.export(tip="count the chunks of a census that hold nothing but the fill")
    def waste(self, plexus, **kwds):
        """
        Count, for each census in my {inputs}, the chunks that hold nothing but the fill and
        would not have been written had the fill been declared and honored: how many there are,
        the bytes they store, and, when the census timed them, what they cost to encode and to
        decode on every read of the whole raster
        """
        # make a channel
        channel = journal.info("qed.measure.waste")
        # the analyses
        census = qed.measurements.census
        # go through the censuses
        for source in self.inputs:
            # the name of the census
            name = self._censusName(source=source)
            # read the summaries
            rows = census.load(source=source)
            # count the chunks
            tally = census.waste(source=source, rows=rows)
            # the summaries by raster name, for the times
            filed = census.groups(rows=rows, key=census.raster)
            # the table
            table = []
            # and its totals
            totals = collections.Counter()
            # go through the rasters by name
            for raster, entry in sorted(tally.items()):
                # the median times of this raster, in ms, if the census took them
                decode, encode = census.medians(
                    rows=filed.get(raster, []), names=("decode_ms", "encode_ms")
                )
                # the seconds spent on the fill chunks, encoding them once and decoding them on
                # every read of the whole raster
                encoding = entry["fill"] * encode / 1e3 if encode is not None else None
                decoding = entry["fill"] * decode / 1e3 if decode is not None else None
                # add the row
                table.append(
                    (
                        raster,
                        entry["rasters"],
                        entry["written"],
                        entry["fill"],
                        entry["fill"] / entry["written"] if entry["written"] else None,
                        entry["fillBytes"] / 2**20,
                        entry["fillBytes"] / entry["stored"] if entry["stored"] else None,
                        entry["checked"],
                        encoding,
                        decoding,
                    )
                )
                # and fold it into the totals
                totals.update({key: value for key, value in entry.items()})
                totals["encoding"] += encoding or 0
                totals["decoding"] += decoding or 0
            # the totals
            table.append(
                (
                    "all",
                    totals["rasters"],
                    totals["written"],
                    totals["fill"],
                    totals["fill"] / totals["written"] if totals["written"] else None,
                    totals["fillBytes"] / 2**20,
                    totals["fillBytes"] / totals["stored"] if totals["stored"] else None,
                    totals["checked"],
                    totals["encoding"] or None,
                    totals["decoding"] or None,
                )
            )
            # the report
            lines = [
                f"# {name}: the chunks that hold nothing but the fill",
                "",
                "A chunk holds nothing but the fill when it has the stored size of the smallest",
                "chunk of its raster and that one is nearly empty; `checked` counts the rasters",
                "whose smallest chunk the census decoded and found to hold one value. The seconds",
                "are the median time per chunk of each raster times the number of chunks.",
                "",
            ]
            # the table
            lines += census.markdown(
                headers=(
                    "raster",
                    "rasters",
                    "written",
                    "fill chunks",
                    "share of written",
                    "fill MiB",
                    "share of stored",
                    "checked",
                    "encode s",
                    "decode s per read",
                ),
                rows=table,
            )
            # publish it
            self._publish(channel=channel, lines=lines, path=f"waste-{name}.md")
        # all done
        return 0

    @qed.export(tip="summarize the results of a census")
    def digest(self, plexus, **kwds):
        """
        Summarize each census in my {inputs}, a folder or the tarball it was packed into: the
        storage settings of its rasters, the percentiles of every measure, the medians by raster,
        by frequency, and by the number of rasters in the product, and the pooled histograms; and
        write the reference data the quality panel compares a raster against, as json
        """
        # make a channel
        channel = journal.info("qed.measure.digest")
        # go through the censuses
        for source in self.inputs:
            # read the summaries
            rows = qed.measurements.census.load(source=source)
            # the name of the census
            name = self._censusName(source=source)
            # and summarize them
            self._publish(
                channel=channel,
                lines=self._digest(name=name, rows=rows),
                path=f"digest-{name}.md",
            )
            # the reference data the quality panel compares a raster against
            path = f"digest-{name}.json"
            # go with them
            with open(path, mode="w") as stream:
                # as json
                json.dump(qed.measurements.census.reference(name=name, rows=rows), stream, indent=1)
            # say where it is
            channel.log(f"reference data written to {os.path.abspath(path)}")
        # all done
        return 0

    @qed.export(tip="compare two censuses scene by scene")
    def compare(self, plexus, **kwds):
        """
        Compare the two censuses in my {inputs} scene by scene: pair the rasters of the same
        name in the products of the same acquisition, and report the medians of every measure on
        both sides, and the share of the pairs in which the second is worse
        """
        # make a channel for the problems that stop the comparison before it starts
        error = journal.error("qed.measure.compare")
        # a comparison takes two
        if len(self.inputs) != 2:
            # so anything else is a mistake
            error.log("a comparison takes two censuses; name them with {inputs}")
            # and bail
            return 1
        # make a channel
        channel = journal.info("qed.measure.compare")
        # the two censuses
        first, second = self.inputs
        # their names
        names = [self._censusName(source=source) for source in (first, second)]
        # read them
        a = qed.measurements.census.load(source=first)
        b = qed.measurements.census.load(source=second)
        # pair their rasters
        matched = qed.measurements.census.pairs(first=a, second=b)
        # the report
        lines = [
            f"# {names[0]} and {names[1]}, scene by scene",
            "",
            f"{len(matched)} pairs of rasters in "
            f"{len({qed.measurements.census.scene(row=x) for x, _ in matched})} scenes; "
            f"{names[0]} has {len(a)} rasters and {names[1]} has {len(b)}",
        ]
        # the comparison of all the pairs, and of the pairs of each frequency
        for label, subset in [("all the pairs", matched)] + sorted(
            (
                (f"frequency {key}", group)
                for key, group in qed.measurements.census.groups(
                    rows=matched,
                    key=lambda row: qed.measurements.census.frequency(row=row[1]),
                ).items()
            )
        ):
            # make room
            lines += ["", f"## {label}, {len(subset)} pairs", ""]
            # and add the table
            lines += qed.measurements.census.markdown(
                headers=(
                    "measure, median over the pairs",
                    names[0],
                    names[1],
                    f"pairs in which {names[1]} is worse (%)",
                ),
                rows=[
                    (label, x, y, None if worse is None else round(100 * worse))
                    for _, label, x, y, worse in qed.measurements.census.compare(matched=subset)
                ],
            )
        # report
        self._publish(channel=channel, lines=lines, path=f"compare-{names[0]}-{names[1]}.md")
        # all done
        return 0

    # implementation details: the analyses
    def _censusName(self, source):
        """
        The name of the census at {source}, from its folder or its tarball
        """
        # the last part of the path
        name = os.path.basename(str(source).rstrip("/"))
        # without the ending of a tarball
        for ending in (".tar.gz", ".tgz"):
            # if it has one
            if name.endswith(ending):
                # strip it
                return name[: -len(ending)]
        # otherwise, it is the name of a folder
        return name

    def _digest(self, name, rows):
        """
        Summarize the census {name} from its {rows}, as the lines of a Markdown report
        """
        # the analyses
        census = qed.measurements.census
        # the measures, by name
        measures = [measure for measure, _, _ in census.MEASURES]
        # the header
        lines = [
            f"# {name}",
            "",
            f"{len(rows)} rasters in {len({row['granule'] for row in rows})} granules",
            "",
            "## Storage settings",
            "",
        ]
        # the settings and how many rasters have each
        lines += census.markdown(
            headers=("setting", "value", "rasters"),
            rows=[
                (setting, value, count)
                for setting, tally in census.settings(rows=rows).items()
                for value, count in tally.most_common()
            ],
        )
        # the percentiles of every measure
        lines += ["", "## Measures", ""]
        lines += census.markdown(
            headers=("measure", "p10", "median", "p90", "max", "rasters"),
            rows=[
                (label, *(census.percentiles(numbers=numbers) or (None,) * 4), len(numbers))
                for numbers, label in (
                    (census.values(rows=rows, name=measure), label)
                    for measure, label, _ in census.MEASURES
                )
            ],
        )
        # the medians by raster, by frequency, and by the number of rasters in the product
        for title, filed in (
            ("By raster", census.groups(rows=rows, key=census.raster)),
            ("By frequency", census.groups(rows=rows, key=census.frequency)),
            ("By the number of rasters in the product", census.rasters(rows=rows)),
        ):
            # make room
            lines += ["", f"## {title}, medians", ""]
            # and add the table
            lines += census.markdown(
                headers=("group", "rasters", *measures),
                rows=[
                    (key, len(group), *census.medians(rows=group, names=tuple(measures)))
                    for key, group in sorted(filed.items())
                ],
            )
        # the pooled histograms
        lines += ["", "## Pooled histograms, counts by tenth of the range", ""]
        lines += census.markdown(
            headers=("histogram", *(f"{10 * i}-{10 * (i + 1)}%" for i in range(10))),
            rows=[
                (label, *census.histogram(rows=rows, name=column))
                for column, label in (
                    ("size_histogram", "stored size of a chunk, share of its raw size"),
                    ("fill_histogram", "share of a page the raster fills"),
                    ("total_histogram", "share of a page all the rasters fill"),
                )
            ],
        )
        # hand off the report
        return lines

    def _present(self, product, cycle):
        """
        Look up my {check} of granules of {product} in {cycle} in my {bucket}, and report how
        many hold their product
        """
        # the AWS client, which qed does not require
        import boto3
        import botocore.exceptions

        # the bucket and the prefix
        bucket, _, prefix = self.bucket.removeprefix("s3://").partition("/")
        # the parser
        registrar = qed.readers.nisar.daac.registrar()
        # the client, with the credentials of the standard AWS chain
        client = boto3.client("s3")
        # the granules to look up
        picked = qed.measurements.scrape.spread(
            scrape=str(self.scrape), product=product, cycle=cycle, count=self.check
        )
        # the ones that hold their product
        present = 0
        # go through them
        for granule in picked:
            # the key of the product
            key = qed.readers.nisar.daac.canonical(
                prefix=prefix, descriptor=registrar.parse(granule)
            )
            # attempt to
            try:
                # look it up
                client.head_object(Bucket=bucket, Key=key)
            # if the bucket said no
            except botocore.exceptions.ClientError as error:
                # because the product is not there
                if error.response.get("Error", {}).get("Code") in ("404", "NoSuchKey", "NotFound"):
                    # it does not count
                    continue
                # anything else is not an answer
                raise
            # otherwise, it counts
            present += 1
        # hand off the count, out of the ones looked up
        return f"{present} of {len(picked)}"

    def _publish(self, channel, lines, path):
        """
        Write the report {lines} to the file at {path}, and to {channel}
        """
        # write the file
        with open(path, mode="w") as stream:
            # a line at a time
            stream.write("\n".join(lines) + "\n")
        # show the report
        for line in lines:
            # a line at a time
            channel.line(line)
        # and say where it is
        channel.line(f"written to {os.path.abspath(path)}")
        # flush
        channel.log()
        # all done
        return

    # implementation details: page occupancy
    def _rasters(self, plexus):
        """
        Enumerate the (reader, dataset) pairs the restrictions allow, without regard to channels
        """
        # the reader restriction
        only = set(self.only)
        # the dataset restriction
        rasters = set(self.rasters)
        # the store is the authority on the connected data sources
        ux = plexus.ux
        # without one
        if ux is None:
            # there are no sources to measure
            return
        # go through the connected readers
        for reader in ux.store.sources:
            # stacks aggregate other products, which are measured on their own
            if isinstance(reader, qed.stacks.stack):
                # so skip them
                continue
            # honor the reader restriction
            if only and reader.pyre_name not in only:
                # by skipping everybody else
                continue
            # make first contact; the layout is metadata, so there is nothing to sample
            reader.open(measure=False)
            # go through the reader's datasets
            for dataset in reader.datasets:
                # honor the dataset restriction
                if rasters and dataset.pyre_name not in rasters:
                    # by skipping everybody else
                    continue
                # publish the pair
                yield reader, dataset
        # all done
        return

    @contextlib.contextmanager
    def _records(self, path, headers):
        """
        Open the file of records at {path} for appending, writing its {headers} on first
        contact, and hand off a writer, or {None} when there is no {path}
        """
        # without a file there is nothing to write to
        if path is None:
            # so hand off nothing
            yield None
            # and bail
            return
        # check whether this is first contact
        fresh = not os.path.exists(path)
        # a compressed file gets a compressed stream; appending adds a member, which readers of
        # the format concatenate
        opener = gzip.open if path.endswith(".gz") else open
        # open the file for appending, so runs accumulate
        with opener(path, mode="at", newline="") as stream:
            # make a writer
            writer = csv.writer(stream)
            # on first contact
            if fresh:
                # write the header
                writer.writerow(headers)
            # hand off the writer
            yield writer
        # all done
        return

    def _occupancy(self, channel, chunks, summaries, host, reader, dataset, layout, tables):
        """
        Record each chunk of {dataset} that was written, and report and summarize how its
        chunks sit on the pages of the file, alone and next to the datasets in {tables}
        """
        # unpack the layout
        pageSize, strategy, _ = layout
        # describe the dataset
        description = qed.readers.pages.describe(dataset=dataset, tables=tables, paging=layout)
        # unpack
        name = description["name"]
        rows, cols = description["storage"]["shape"]
        tileRows, tileCols = description["storage"]["tile"]
        raw = description["raw"]
        grid = description["grid"]
        storage = description["storage"]
        record = description["record"]
        nodata = description["nodata"]
        # go through its chunks, unless nobody wants them one by one
        for address, size, (row, col) in tables[name] if chunks is not None else ():
            # the pages it spans, when the file has pages
            first = address // pageSize if pageSize else 0
            last = (address + size - 1) // pageSize if pageSize else 0
            # record it
            chunks.writerow(
                (host, name, row, col, address, size, raw, pageSize, first, last - first + 1)
            )
        # sign on
        channel.line(f"{name}:")
        channel.line(f"  file: {strategy} strategy, pages of {pageSize / 2**20:g} MiB")
        channel.line(
            f"  storage: {rows}x{cols} {storage['cell']} in chunks of {tileRows}x{tileCols}, "
            f"filters: {', '.join(storage['filters']) or 'none'}"
        )
        # if nothing was written
        if not record["written"]:
            # there is nothing else to say
            channel.line(f"  none of its {grid} chunks were written")
            # so bail
            return
        # report the chunk table
        channel.line(
            f"  chunks: {record['written']} of {grid} written ({record['written'] / grid:.0%}), "
            f"{record['stored'] / 2**20:.1f} MiB stored"
        )
        # the sizes, against the raw chunk
        channel.line(
            f"  chunk size: raw {raw / 2**20:.2f} MiB; stored median "
            f"{record['median'] / 2**20:.2f} MiB, from {record['smallest'] / 2**10:.1f} KiB "
            f"to {record['largest'] / 2**20:.2f} MiB; compression {record['compression']:.2f}x"
        )
        # the chunks that hold next to nothing
        channel.line(
            f"  nearly empty: {record['empty']} chunks "
            f"({record['empty'] / record['written']:.0%}) store less than "
            f"{qed.readers.pages.NEARLY_EMPTY:.0%} of their raw size, "
            f"{record['emptyStored'] / 2**20:.1f} MiB in all"
        )
        # the fill the library knows about, and the one the conventions of the format declare
        channel.line(
            f"  fill: the library's is {nodata['hdf5']} ({nodata['status']}); "
            f"the '_FillValue' attribute says {nodata['cf']}"
        )
        # what the smallest chunk holds
        channel.line(
            f"  the smallest chunk holds {nodata['found']}"
            + (
                f"; decoding it takes {nodata['decode'] * 1e3:.2f} ms, making it from its value "
                f"{nodata['make'] * 1e3:.3f} ms"
                if nodata["decode"] is not None
                else ""
            )
        )
        # the chunks that hold nothing but the value of the smallest one
        if nodata["fillChunks"] is not None:
            # report them
            channel.line(
                f"  {nodata['fillChunks']} chunks hold only {nodata['found']}, "
                f"{nodata['fillBytes'] / 2**20:.2f} MiB; {nodata['verified']} of 2 checked; "
                + (
                    f"encoding one at deflate level {nodata['level']} takes "
                    f"{nodata['encode'] * 1e3:.2f} ms"
                    if nodata["level"] is not None
                    else "no deflate level reproduces them"
                )
            )
        # and what a typical chunk of data costs to decode
        if nodata["data"] is not None:
            # report it
            channel.line(f"  decoding the median chunk of data takes {nodata['data'] * 1e3:.2f} ms")
        # and the distribution of the sizes
        channel.line("  stored size, as a share of the raw size:")
        # one bin per line
        for line in qed.readers.pages.bars(counts=record["sizes"]):
            # indented under its title
            channel.line(f"    {line}")
        # a file without pages is read in byte ranges, so the rest does not apply
        if not pageSize:
            # say so
            channel.line("  the file is not paged; a reader fetches each chunk as one range")
            # summarize what there is
            self._summarize(
                summaries=summaries,
                host=host,
                reader=reader,
                strategy=strategy,
                storage=storage,
                nodata=nodata,
                record=record,
            )
            # and bail
            return
        # the spans
        spans = record["spans"]
        # report them
        channel.line(
            "  pages per chunk: "
            + ", ".join(
                f"{'3+' if key == 3 else key}: {count} ({count / record['written']:.0%})"
                for key, count in sorted(spans.items())
            )
        )
        # the datasets that share its pages
        partners = ", ".join(
            f"{other} ({share / 2**20:.0f} MiB)"
            for other, share in sorted(record["partners"].items(), key=lambda item: -item[1])
        )
        # report the amplification of every way of reading it
        channel.line(
            f"  read amplification: {record['alone']:.2f}x reading one chunk at a time, "
            f"{record['once']:.2f}x reading every chunk with each page fetched once"
        )
        # and next to its partners
        channel.line(
            f"    {record['joint']:.2f}x reading it together with the datasets that share its "
            f"pages: {partners or 'none'}"
        )
        # the occupancy of the pages that hold any of this dataset
        channel.line(
            f"  pages: {record['pages']} hold part of it; it fills a median of "
            f"{record['fillMedian']:.0%} and a mean of {record['fillMean']:.0%} of each, and "
            f"{record['fillFull']:.0%} of them at least 90%; all datasets together fill a mean "
            f"of {record['totalMean']:.0%}"
        )
        # the distribution of its share of the pages
        channel.line("  its share of each page:")
        # one bin per line
        for line in qed.readers.pages.bars(counts=record["fill"]):
            # indented under its title
            channel.line(f"    {line}")
        # and the share of all datasets together
        channel.line("  the share of all datasets together:")
        # one bin per line
        for line in qed.readers.pages.bars(counts=record["total"]):
            # indented under its title
            channel.line(f"    {line}")
        # how crowded they are
        channel.line(f"  tenants: a median of {record['tenants']:g} chunks per page")
        # and whether the chunks that share a page are neighbors on the raster
        locality = record["locality"]
        # report it
        channel.line(
            "  locality: "
            + (
                "no page holds two of its chunks"
                if locality is None
                else f"{locality:.0%} of the consecutive chunks on a page are raster neighbors"
            )
        )
        # summarize
        self._summarize(
            summaries=summaries,
            host=host,
            reader=reader,
            strategy=strategy,
            storage=storage,
            nodata=nodata,
            record=record,
        )
        # all done
        return

    def _summarize(self, summaries, host, reader, strategy, storage, nodata, record):
        """
        Add the summary {record} of a dataset of {reader}, with its {storage} and what it holds
        where there is nothing in {nodata}, to the file of {summaries}
        """

        # the histograms, compactly, as the counts of their bins
        def bins(counts):
            """
            Render the {counts} of a histogram, or nothing when there is no histogram
            """
            # join them, if there are any
            return "|".join(map(str, counts)) if counts is not None else ""

        # the datasets that share its pages, compactly
        partners = ";".join(
            f"{other}:{share}" for other, share in sorted(record.get("partners", {}).items())
        )
        # write the row
        summaries.writerow(
            (
                host,
                reader.uri,
                record["dataset"],
                strategy,
                record["pageSize"],
                record["grid"],
                record["written"],
                record["stored"],
                record["raw"],
                record["compression"],
                record["empty"],
                record.get("pages"),
                record.get("alone"),
                record.get("once"),
                record.get("joint"),
                partners,
                record.get("fillMedian"),
                record.get("fillMean"),
                record.get("fillFull"),
                record.get("totalMean"),
                record.get("tenants"),
                record.get("locality"),
                storage["bytes"],
                storage["shape"][0],
                storage["shape"][1],
                storage["tile"][0],
                storage["tile"][1],
                storage["cell"],
                ">".join(storage["filters"]),
                bins(record.get("sizes")),
                bins(record.get("fill")),
                bins(record.get("total")),
                record["emptyStored"],
                record.get("emptyPages"),
                nodata["status"],
                nodata["hdf5"],
                nodata["cf"],
                nodata["found"],
                nodata["decode"],
                nodata["make"],
                nodata["data"],
                nodata["fillChunks"],
                nodata["fillBytes"],
                nodata["verified"],
                nodata["level"],
                nodata["encode"],
            )
        )
        # all done
        return

    # implementation details: the whole dataset pass
    def _thumbnail(self, dataset):
        """
        Lay out the whole-dataset pass the way the minimap thumbnail does: decimate until
        the long axis fits my {resolution}, then chop into slices of the dataset's own tile
        """
        # unpack the extent
        shape = tuple(dataset.shape)
        # pick the decimation that brings the long axis down to the target
        exp = max(0, int(math.log2(max(shape) / self.resolution)))
        # deduce the stride
        stride = 2**exp
        # form the decimated extent; floor division keeps the footprint in bounds
        decimated = [extent // stride for extent in shape]
        # the slice unit is the dataset's preferred tile, which is the chunk shape for
        # products that have one, so no chunk is decompressed by two different workers
        unit = tuple(dataset.tile)
        # collect the slices
        slices = []
        # walk the decimated raster
        for row in range(0, decimated[0], unit[0]):
            # the rows this slice covers
            height = min(unit[0], decimated[0] - row)
            # and its columns
            for col in range(0, decimated[1], unit[1]):
                # the columns this slice covers
                width = min(unit[1], decimated[1] - col)
                # record it
                slices.append((row, col, height, width))
        # hand off the geometry
        return exp, slices

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
                discovery = qed.timers.wall(f"qed.profiler.discovery.{reader.pyre_name}").ms()
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
                channel.line(f"  {dataset.pyre_name}.{name}: {span}x{span} @ zoom {zoom}")
                # the clocks of the trials
                wallclock = qed.timers.wall("qed.measure.tile.wall")
                cpuclock = qed.timers.cpu("qed.measure.tile.cpu")
                # repeat the point
                for trial in range(self.trials):
                    # start both clocks afresh
                    wallclock.reset()
                    cpuclock.reset()
                    wallclock.start()
                    cpuclock.start()
                    # render the tile through the full pipeline, encoder included
                    dataset.render(
                        channel=pipeline,
                        zoom=(zoom, zoom),
                        origin=self._origin(dataset=dataset, span=span, zoom=zoom),
                        shape=(span, span),
                    )
                    # stop the clocks
                    wallclock.stop()
                    cpuclock.stop()
                    # and read them
                    wall = wallclock.ms()
                    cpu = cpuclock.ms()
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
                    f"--rasters={dataset.pyre_name}",
                    f"--channels={name}",
                    f"--shapes={exponent},{exponent + 1}",
                    f"--zooms={zoom},{zoom + 1}",
                    "--trials=1",
                    "--cache=fresh",
                    "--cold=no",
                    f"--sample={'yes' if self.sample else 'no'}",
                    f"--output={self.output}",
                ]
                # the tile is picked here, so the search for data never warms the child
                row, col = self._origin(dataset=dataset, span=span, zoom=zoom)
                # and handed to it explicitly
                cmd.append(f"--corner={row},{col}")
                # show me
                channel.line(
                    f"fresh: {dataset.pyre_name}.{name}: {span}x{span} @ zoom {zoom}, "
                    f"origin {row}x{col}"
                )
                # launch and wait
                got = subprocess.run(cmd)
                # if the point failed
                if got.returncode != 0:
                    # a missing point silently skews the fit, so make it loud
                    warning = journal.warning("qed.measure.tile")
                    warning.log(
                        f"point failed: {dataset.pyre_name}.{name} " f"{span}x{span} @ zoom {zoom}"
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
        # the dataset restriction
        rasters = set(self.rasters)
        # the plexus hands its readers to the ux store when the store is built, so the store is the
        # authority on the connected data sources; without ux support there is nothing to do
        ux = plexus.ux
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
            # which also charges the discovery and stats timers this panel reports, and
            # samples the datasets only if asked to
            reader.open(measure=self.sample)
            # go through the reader's datasets
            for dataset in reader.datasets:
                # honor the dataset restriction
                if rasters and dataset.pyre_name not in rasters:
                    # by skipping everybody else
                    continue
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
                # find the tile this point renders
                row, col = self._origin(dataset=dataset, span=span, zoom=zoom)
                # a tile that hangs over the raster edge crashes the native pipeline
                if (
                    row < 0
                    or col < 0
                    or (row + span) * 2**zoom > rows
                    or (col + span) * 2**zoom > cols
                ):
                    # so skip points that don't fit
                    continue
                # publish the point
                yield span, zoom
        # all done
        return

    def _origin(self, dataset, span, zoom):
        """
        Pick the origin of the {span} tile at {zoom}, in decimated coordinates: the one i was
        given, or else the tile of the client's grid that holds the anchor of the raster
        """
        # an explicit origin wins
        if self.corner is not None:
            # as is
            return tuple(self.corner)
        # otherwise, find the extent of the raster at this zoom
        extents = [axis >> zoom for axis in dataset.shape]
        # and where its anchor lands
        anchor = [cell >> zoom for cell in self._anchor(dataset=dataset)]
        # the client lays its tiles on a grid of {span} from the corner, so pick the one that
        # holds the anchor, stepping back when it would hang over the far edge
        origin = tuple(
            min(cell // span * span, extent - span) // span * span
            for cell, extent in zip(anchor, extents)
        )
        # all done
        return origin

    def _anchor(self, dataset):
        """
        Find a cell of {dataset} that holds data, as near its center as the sample windows allow

        A geocoded product frames its data in fill, and a tile of nothing but fill is
        answered without reading anything, so a measurement has to be aimed at the data. The
        search reads a window at a time, one chunk each, nearest the center first
        """
        # the anchors found so far, by dataset
        if self._anchors is None:
            # start the memo on first use
            self._anchors = {}
        # a dataset searched before
        name = dataset.pyre_name
        # has its anchor ready
        if name in self._anchors:
            # so hand it off
            return self._anchors[name]
        # unpack the extent
        rows, cols = tuple(dataset.shape)
        # the center, where the measurement goes if no window finds data
        anchor = (rows // 2, cols // 2)
        # the window is the preferred tile, kept inside the raster
        span = tuple(min(width, axis) for width, axis in zip(tuple(dataset.tile), (rows, cols)))
        # plan a fine grid of windows over the extent, nearest the center first
        candidates = sorted(
            qed.readers.windows(dataset=dataset, stops=16),
            key=lambda o: (o[0] + span[0] / 2 - rows / 2) ** 2
            + (o[1] + span[1] / 2 - cols / 2) ** 2,
        )
        # go through them
        for origin in candidates:
            # read one at full resolution
            count, *_ = dataset.sample(zoom=(0, 0), origin=origin, shape=span)
            # the first one that holds data
            if count > 0:
                # anchors the measurement at its center
                anchor = (origin[0] + span[0] // 2, origin[1] + span[1] // 2)
                # and ends the search
                break
        # if none did
        else:
            # the measurement will be of fill, so say so
            warning = journal.warning("qed.measure")
            warning.log(f"found no data in '{name}'; measuring at its center")
        # remember it
        self._anchors[name] = anchor
        # and hand it off
        return anchor

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
                channel.line(f"    b: {b * 1e6:.1f} ns per unit ({1 / (b * 1000):.1f} M/s)")
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
    def _grid(self, dataset, span, zoom, count):
        """
        Lay out up to {count} distinct in-bounds tile origins, in decimated coordinates,
        nearest the anchor of the raster first
        """
        # unpack the raster shape
        rows, cols = dataset.shape
        # reduce it to the decimated extents at this zoom
        decRows = rows >> zoom
        decCols = cols >> zoom
        # the anchor, in the same coordinates
        center = tuple(cell / 2**zoom for cell in self._anchor(dataset=dataset))
        # the server samples these windows at first contact, on one of its crew members, so a
        # tile that covers any of them would be served out of that member's caches
        probed = self._probed(dataset=dataset)
        # every tile of the client's grid that fits inside the raster and stays clear of them
        origins = [
            (r, c)
            for r in range(0, decRows - span + 1, span)
            for c in range(0, decCols - span + 1, span)
            if not any(
                r << zoom < wr + wh
                and wr < (r + span) << zoom
                and c << zoom < wc + ww
                and wc < (c + span) << zoom
                for wr, wc, wh, ww in probed
            )
        ]
        # a geocoded product frames its data in fill, whose tiles would fetch nothing, so take
        # the tiles closest to the anchor; the square distance of the tile center decides
        origins.sort(
            key=lambda o: (o[0] + span / 2 - center[0]) ** 2 + (o[1] + span / 2 - center[1]) ** 2
        )
        # publish as many as were asked for
        yield from origins[:count]
        # all done
        return

    def _void(self, dataset, span, zoom, count):
        """
        Lay out up to {count} distinct in-bounds tile origins, in decimated coordinates, whose
        footprint holds no chunk that was written, so that producing them reads nothing
        """
        # the chunk table of the dataset, as the library sees it
        table = dataset.data.dataset.chunkTable()
        # a dataset that is not stored in chunks
        if table is None:
            # has no holes
            return
        # the origins of the chunks that were written
        written = {tuple(chunk.origin) for chunk in table}
        # unpack the shape of a chunk
        tileRows, tileCols = tuple(dataset.tile)
        # unpack the raster shape
        rows, cols = dataset.shape
        # the footprint of a tile at full resolution
        extent = span << zoom
        # the number of tiles laid out so far
        found = 0
        # go through the tiles of the client's grid that fit inside the raster
        for r in range(0, (rows >> zoom) - span + 1, span):
            for c in range(0, (cols >> zoom) - span + 1, span):
                # the chunks under the footprint
                under = (
                    (row, col)
                    for row in range(
                        (r << zoom) // tileRows * tileRows, (r << zoom) + extent, tileRows
                    )
                    for col in range(
                        (c << zoom) // tileCols * tileCols, (c << zoom) + extent, tileCols
                    )
                )
                # a tile over any chunk that was written
                if any(chunk in written for chunk in under):
                    # reads something, so skip it
                    continue
                # publish the rest
                yield (r, c)
                # count it
                found += 1
                # and stop when there are enough
                if found == count:
                    # of them
                    return
        # all done
        return

    def _probed(self, dataset):
        """
        The windows of {dataset} the probe samples when the server makes first contact, as
        (row, col, height, width) at full resolution; a flavor that tunes itself some other way
        loses nothing but a few candidate tiles by staying clear of them too
        """
        # the window is the preferred tile, kept inside the raster, just as the probe has it
        height, width = (min(w, a) for w, a in zip(tuple(dataset.tile), tuple(dataset.shape)))
        # the probe plans its windows with its own default density, and so does this
        windows = [(r, c, height, width) for r, c in qed.readers.windows(dataset=dataset)]
        # all done
        return windows

    def _launch(self, reader, cache=False):
        """
        Launch the installed qed server with the swarm configuration, with its tile {cache} on
        or off
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
            # with the requested team size for the target reader
            f"--qed.app.nexus.services.web.fleet.{reader.pyre_name}.size={self.team}",
            # building the levels of the product, unless asked not to
            f"--qed.app.pyramids={'yes' if self.levels else 'no'}",
        ]
        # unless asked for it
        if not cache:
            # the tile cache is off, so every request is an actual render
            cmd.append("--qed.app.nexus.services.web.fleet.cache.capacity=0")
        # launch
        process = subprocess.Popen(
            cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT
        )
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

    def _select(self, reader, dataset, channel):
        """
        Drive the server side view state to the target {reader}, {dataset}, and {channel}
        """
        # the server boots without touching any data file, so its catalog is empty until a
        # client declares it relevant; ask it to stage, the way the viz activity does
        self._stage()
        # select the reader in viewport 0
        self._graphql(
            query=(
                f"mutation {{ viewReaderSelect(input: {{viewport: 0, "
                f'reader: "{reader.pyre_name}"}}) {{ view {{ dataset {{ name }} }} }} }}'
            )
        )
        # a product whose axes are not all single valued does not resolve from the reader
        # selection alone, so pin each axis to the coordinate that identifies my target
        for axis, value in dict(dataset.selector).items():
            # read back what the view currently holds for this axis
            reply = self._graphql(query="{ qed { views { selections { name value } } } }")
            # unpack the selections of viewport 0
            current = {
                entry["name"]: entry["value"]
                for entry in reply["data"]["qed"]["views"][0]["selections"]
            }
            # an axis already sitting on the value i want needs no help; toggling it would
            # clear the selection rather than confirm it
            if current.get(axis) == value:
                # so leave it alone
                continue
            # otherwise, pin it
            self._graphql(
                query=(
                    f"mutation {{ viewCoordinateToggle(input: {{viewport: 0, "
                    f'reader: "{reader.pyre_name}", selector: "{axis}", '
                    f'value: "{value}"}}) {{ view {{ dataset {{ name }} }} }} }}'
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

    def _stage(self):
        """
        Ask the launched server to establish first contact with its data sources, and wait
        for the surveys to land
        """
        # ask
        self._graphql(query="mutation { stage(input: {}) { readers { name } } }")
        # the surveys run on the crews, so the answer arrives later; wait for it
        for _ in range(600):
            # read the catalog
            reply = self._graphql(query="{ qed { readers { name status } } }")
            # unpack the standings
            rows = reply["data"]["qed"]["readers"]
            # a source that failed will never become ready, so stop waiting on the pile
            # once nobody is still working
            if all(row["status"] in ("ready", "failed") for row in rows):
                # everybody has settled
                return True
            # otherwise, wait a beat
            time.sleep(0.5)
        # the surveys never settled
        warning = journal.warning("qed.measure")
        # say so
        warning.log("the launched server never finished staging its sources")
        # and report it
        return False

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
        Fetch all {urls} with {workers} concurrent clients on the pyre event loop; return the
        batch wall time in ms, the per-request latencies of the successes, and the failure
        count
        """
        # the event loop that drives the clients
        selector = pyre.ipc.newSelector(name="qed.measure.swarm")
        # the tiles, as request paths, in a queue the clients share
        queue = collections.deque(urllib.parse.urlsplit(url).path for url in urls)
        # the clients that have not run out of tiles yet
        busy = set()

        # when a client runs out of tiles
        def done(client):
            """
            Note that {client} has run out of tiles, and stop the loop after the last one
            """
            # it is no longer busy
            busy.discard(client)
            # and once nobody is
            if not busy:
                # the batch is over
                selector.stop()
            # all done
            return

        # make the clients
        clients = [
            TileClient(
                index=index,
                host="127.0.0.1",
                port=self.port,
                selector=selector,
                queue=queue,
                patience=self._tilePatience,
                onDone=done,
            )
            for index in range(workers)
        ]
        # they are all busy until they say otherwise
        busy.update(clients)
        # the clock of the batch
        clock = qed.timers.wall("qed.measure.swarm.batch")
        # started afresh
        clock.reset()
        clock.start()
        # set every client going
        for client in clients:
            # each takes its first tile
            client.start()
        # unless the queue was too short to keep anybody busy
        if busy:
            # drive them until the last one runs dry
            selector.watch()
        # stop the clock
        clock.stop()
        # collect the latencies of every client
        latencies = [latency for client in clients for latency in client.latencies]
        # and their failures
        failures = sum(client.failures for client in clients)
        # all done
        return clock.ms(), latencies, failures

    def _stop(self, process, log):
        """
        Bring the launched server down and close its log
        """
        # attempt to
        try:
            # ask it to shut down
            with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/stop", timeout=5):
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
                f"{span}x{span} @ zoom {zoom}, {self.workload}, team of {self.team}:"
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
                        self.workload,
                    )
                )
                # and report it
                channel.line(
                    f"  {workers:4} clients: {rate:6.1f} tiles/s, "
                    f"speedup {speedup:4.2f}, median {median:.1f} ms, p95 {p95:.1f} ms"
                )
        # all done
        return

    # implementation details: the s3 program
    def _s3port(self):
        """
        Check that my {port} is free for the servers the swarms launch
        """
        # make a socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            # attempt to
            try:
                # claim the port
                probe.bind(("127.0.0.1", self.port))
            # if somebody else has it
            except OSError:
                # it is not free
                return False
        # otherwise, it is
        return True

    def _results(self, kind="measure"):
        """
        The directory that collects the results: my {results}, or one named after the {kind}
        of run, the host, and the time
        """
        # if one was named
        if self.results is not None:
            # use it
            return self.results.resolve()
        # otherwise, stamp one with the kind of run, the host, and the time
        stamp = f"qed-{kind}-{self.pyre_host.nickname}-{datetime.datetime.now():%Y%m%d-%H%M%S}"
        # in the current directory
        return qed.primitives.path(stamp).resolve()

    def _about(self, channel, results):
        """
        Record the versions and revisions of qed and the pyre underneath it in {results}
        """
        # what qed says about its libraries and bindings, from the installation the
        # measurements run
        about = subprocess.run(
            ["qed", "--shell=script", "about", "version"],
            cwd=results,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
        )
        # and the pyre this process runs on, which is the one the measurements load as well
        version = ".".join(map(str, pyre.meta.version[:3]))
        # assemble the record
        record = about.stdout + about.stderr + f"pyre: {version} rev {pyre.meta.revision}\n"
        # keep it
        with open(results / "about.txt", mode="w") as stream:
            # all of it
            stream.write(record)
        # show it
        for line in record.splitlines():
            # one line at a time
            channel.line(line)
        # flush
        channel.log()
        # all done
        return

    def _configure(self, directory, uri, flavor):
        """
        Write the configuration the measurements read into {directory}: the granule at {uri}
        and its {flavor} of reader, and nothing else, since the credentials come from the
        standard AWS chain
        """
        # the settings
        settings = (
            "# -*- yaml -*-\n"
            "\n"
            "# the granule under measurement\n"
            "product:\n"
            f"    uri: {uri}\n"
            "\n"
            "# register it\n"
            "datasets:\n"
            f"    - nisar.{flavor}#product\n"
        )
        # write them
        with open(directory / "qed.yaml", mode="w") as stream:
            # all at once
            stream.write(settings)
        # all done
        return

    def _s3survey(self):
        """
        Open my {granule} and list its datasets as (name, shape, tile, channels)
        """
        # build the reader the way the configuration does; {flavor} is one of the readers
        # its validator allows
        reader = getattr(qed.readers.nisar, self.flavor)(name="product", uri=self.granule)
        # make first contact, without the statistics
        reader.open(measure=False)
        # describe each dataset
        found = [
            (
                dataset.pyre_name,
                tuple(dataset.shape),
                tuple(dataset.tile),
                tuple(dataset.channels.keys()),
            )
            for dataset in reader.datasets
        ]
        # let go of the granule, so its handles close before the measurements start
        del reader
        # hand off the description
        return found

    def _s3pick(self, datasets):
        """
        Choose the dataset and channel to measure: the first of my {rasters} and {channels}, or
        else the largest dataset, preferring one with an amplitude channel, and its amplitude or
        its first channel
        """
        # make a channel for what the granule lacks
        error = journal.error("qed.measure.s3")
        # if a dataset was named
        if self.rasters:
            # the name, with or without the name of the granule in front
            wanted = self.rasters[0]
            # find it
            chosen = [entry for entry in datasets if entry[0] in (wanted, f"product.{wanted}")]
            # a dataset the granule does not have is a mistake
            if not chosen:
                # so say so
                error.log(f"the granule has no dataset '{wanted}'")
                # and give up
                return None
            # otherwise, it is the one
            name, _, _, channels = chosen[0]
        # otherwise
        else:
            # rank the datasets: amplitude first, then size
            name, _, _, channels = max(
                datasets, key=lambda entry: ("amplitude" in entry[3], entry[1][0] * entry[1][1])
            )
        # if a channel was named
        if self.channels:
            # it is the one
            pipeline = self.channels[0]
            # but a channel the dataset does not have is a mistake
            if pipeline not in channels:
                # so say so
                error.log(f"'{name}' has no channel '{pipeline}'; it has {channels}")
                # and give up
                return None
        # otherwise
        else:
            # amplitude if there is one, else the first
            pipeline = "amplitude" if "amplitude" in channels else channels[0]
        # hand off the choice
        return name, pipeline

    def _s3run(self, channel, results, label, args, failures):
        """
        Run one measurement in a fresh process from {results}, passing its output to {channel}
        and noting a failure in {failures} instead of abandoning the measurements to come
        """
        # say what is starting
        channel.log(label)
        # launch the panel from the results directory, so the child reads its configuration
        process = subprocess.Popen(
            ["qed", "--shell=script", "measure", *args],
            cwd=results,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        # pass its output along as it arrives
        self._s3relay(channel=channel, process=process)
        # wait for it to finish
        status = process.wait()
        # if it failed
        if status != 0:
            # say so
            channel.log(f"{label} failed with status {status}")
            # and remember it for the summary
            failures.append(label)
        # all done
        return

    def _s3relay(self, channel, process):
        """
        Pass the output of the child {process} to {channel} as it arrives, one entry for each
        entry the child makes, so the console and the run log see it as it happens
        """
        # watch the output of the child
        watcher = selectors.DefaultSelector()
        # for something to read
        watcher.register(process.stdout, selectors.EVENT_READ)
        # the lines of the entry being assembled
        entry = []
        # and whatever trails the last complete line
        pending = b""
        # until the child closes its output
        while True:
            # wait a little for more
            ready = watcher.select(timeout=self._s3quiet)
            # if the child has been quiet for that long
            if not ready:
                # what it said so far is a whole entry
                self._s3flush(channel=channel, entry=entry)
                # and wait some more
                continue
            # read what is there
            chunk = os.read(process.stdout.fileno(), 1 << 16)
            # if there is nothing, the child is done
            if not chunk:
                # so stop listening
                break
            # split off the complete lines, keeping the tail for the next read
            *lines, pending = (pending + chunk).split(b"\n")
            # go through the complete ones
            for line in lines:
                # decode it
                text = line.decode(errors="replace")
                # a line that is not indented opens a new entry of the child
                if text and not text[0].isspace():
                    # so whatever came before it is a whole entry
                    self._s3flush(channel=channel, entry=entry)
                # add the line to the entry being assembled
                entry.append(text)
        # a last line without a newline still belongs to the output
        if pending:
            # so keep it
            entry.append(pending.decode(errors="replace"))
        # and flush whatever is left
        self._s3flush(channel=channel, entry=entry)
        # stop watching
        watcher.close()
        # all done
        return

    def _s3flush(self, channel, entry):
        """
        Emit the lines of {entry} as one entry of {channel}, and empty it
        """
        # if there is nothing to say
        if not entry:
            # say nothing
            return
        # go through the lines
        for line in entry:
            # add each one
            channel.line(line)
        # make the entry
        channel.log()
        # and start over
        entry.clear()
        # all done
        return

    def _pack(self, channel, results):
        """
        Pack the {results} directory into a tarball next to it
        """
        # the tarball
        tarball = results.parent / f"{results.name}.tar.gz"
        # make it
        with tarfile.open(tarball, mode="w:gz") as archive:
            # with the whole directory, under its own name, leaving out the workspaces of the
            # servers, whose levels and caches are derived from the product and can be huge
            archive.add(
                str(results),
                arcname=results.name,
                filter=lambda entry: None if ".qed" in entry.name.split("/") else entry,
            )
        # say where it is
        channel.log(f"results packed in {tarball}")
        # all done
        return

    # implementation details: the pyramid
    def _build(self, reader, dataset, team, directory):
        """
        Build the pyramid of {dataset}, and of the rasters it is read with, on a crew of {team}
        members working out of {directory}, and time it, as the seconds until the dataset is
        seeded, the seconds until every build is done, and the state they ended in
        """
        # the workspace the levels go into
        workspace = qed.workspaces.local(name=f"qed.measure.pyramid.team{team}.workspace")
        # is the folder of this build
        workspace.path = str(directory)
        # the fleet, with an event loop of its own
        fleet = qed.nexus.fleet(name=f"qed.measure.pyramid.team{team}")
        fleet.dispatcher = pyre.ipc.newPSL()
        # whose crews are forked by the helper, and whose journal is heard on its event loop
        fleet.recruiter = qed.nexus.forkserver()
        fleet.recruiter.start(dispatcher=fleet.dispatcher)
        # the team of the reader, with the size under measurement
        fleet.team(reader=reader.pyre_name).size = team
        # the clock of the build
        clock = qed.timers.wall(f"qed.measure.pyramid.team{team}")
        # the times, unknown until they happen
        marks = {"seeded": None, "ready": None}
        # and the reasons of any failures
        errors = []
        # the builds, one per raster
        builds = []

        # when the dataset is worth looking at
        def seeded(build):
            """
            The first tiles of the dataset have reported
            """
            # note when
            marks["seeded"] = clock.sec()
            # all done
            return

        # when a build is over
        def over(build, error=None):
            """
            A build is done, or failed with {error}; once they all are, the loop stops
            """
            # a failure
            if error is not None:
                # has its reason noted
                errors.append(str(error))
            # once every build is over
            if all(build.done for build in builds):
                # note when
                marks["ready"] = clock.sec()
                # and stop the loop
                fleet.dispatcher.stop()
            # all done
            return

        # when the build takes too long
        def overdue(timestamp):
            """
            The build has taken longer than its patience allows

            N.B.: this is an alarm handler; returning {None} keeps it from being rescheduled
            """
            # note it
            errors.append(f"gave up after {self._buildPatience} s")
            # and stop the loop
            fleet.dispatcher.stop()
            # the alarm is done
            return None

        # the rasters: the dataset, and the ones it is read with, since a masked render reads
        # all of them at one depth or none of them
        rasters = [dataset] + list(dataset.companions().values())
        # go through them
        for raster in rasters:
            # the pyramid, laid out in the workspace
            pyramid = qed.readers.nisar.pyramid(reader=reader, dataset=raster, workspace=workspace)
            # and its build; only the dataset reports its seed, as it does in the server
            builds.append(
                qed.nexus.build(
                    reader=reader,
                    dataset=raster,
                    pyramid=pyramid,
                    fleet=fleet,
                    statistics=qed.ux.sample(),
                    onSeeded=seeded if raster is dataset else None,
                    onDone=over,
                    onFailed=over,
                )
            )
        # start the clock
        clock.reset()
        clock.start()
        # start the builds
        for build in builds:
            # each hands out its first level
            build.start()
        # give up if they take too long
        fleet.dispatcher.alarm(interval=self._buildPatience * second, call=overdue)
        # unless they are over already
        if not all(build.done for build in builds):
            # run the loop until they are
            fleet.dispatcher.watch()
        # stop the clock
        clock.stop()
        # let the crew go
        fleet.disband()
        # the state the builds ended in
        status = "; ".join(errors) if errors else "ready"
        # hand off the times and the state
        return marks["seeded"], (marks["ready"] if not errors else None), status

    # implementation details: tiles during a build
    def _view(self, plexus, reader, dataset, channel):
        """
        Point the view of viewport 0 at {dataset} of {reader} and its {channel}, the way the
        client would, and hand it back, or {None} if it did not land there

        The store of this process has no fleet, so pointing a view does not start a build
        """
        # get the store
        store = plexus._ux.store
        # select the reader
        store.selectSource(viewport=0, name=reader.pyre_name)
        # the view was made before the reader discovered its datasets, so let it catch up
        store.view(viewport=0).refresh()
        # a product whose axes are not all single valued does not resolve from the reader
        # selection alone, so pin each axis to the coordinate that identifies the dataset
        for axis, value in dict(dataset.selector).items():
            # an axis already sitting on the value i want needs no help; toggling it would
            # clear the selection rather than confirm it
            if store.view(viewport=0).selections.get(axis) == value:
                # so leave it alone
                continue
            # otherwise, pin it
            store.toggleCoordinate(viewport=0, source=reader.pyre_name, axis=axis, coordinate=value)
        # pick the channel; the store hands back the views it touched as it goes
        for _ in store.channelSet(viewport=0, source=reader.pyre_name, tag=channel):
            # and there is nothing to do with them
            pass
        # get the view
        view = store.view(viewport=0)
        # if it did not land on the dataset
        if view.dataset is None or view.dataset.pyre_name != dataset.pyre_name:
            # say so
            return None
        # otherwise, hand it off
        return view

    def _contend(self, reader, dataset, name, view, directory):
        """
        Build the pyramid of {dataset}, and of the rasters it is read with, on a crew of {team}
        members working out of {directory}, ask the same crew for tiles of its {name} channel at
        a steady rate while it builds, and again once it is done; hand back the seconds until the
        dataset is seeded and until the build is done, the state it ended in, and a record of
        every tile, as (phase, seconds since the start, latency in ms, failure)
        """
        # the workspace the levels go into
        workspace = qed.workspaces.local(name=f"qed.measure.contention.team{self.team}.workspace")
        # is the folder of this build
        workspace.path = str(directory)
        # the fleet, with an event loop of its own
        fleet = qed.nexus.fleet(name=f"qed.measure.contention.team{self.team}")
        fleet.dispatcher = pyre.ipc.newPSL()
        # the team of the reader, with the size under measurement
        fleet.team(reader=reader.pyre_name).size = self.team
        # the clock of the run
        clock = qed.timers.wall(f"qed.measure.contention.team{self.team}")
        # the geometry of the tiles
        span = 2 ** self.shapes[0]
        zoom = self.zooms[0]
        # distinct tiles for both phases, so that neither is served from the caches the other
        # warmed up, taken alternately from the tiles nearest the data, so that both phases
        # sample the same neighborhood; the build takes as many as it lasts for
        origins = list(self._grid(dataset=dataset, span=span, zoom=zoom, count=self._crowd))
        # split between the phases
        queues = {
            "build": collections.deque(origins[0::2]),
            "after": collections.deque(origins[1::2][: self.tiles]),
        }
        # the time between tiles
        interval = 1 / self.rate
        # the record of every tile
        records = []
        # the state of the run: the phase, the tiles in flight, and the times of the build
        state = {"phase": "build", "flight": 0, "seeded": None, "ready": None}
        # the reasons of any failures of the build
        errors = []
        # the builds, one per raster
        builds = []

        # ask for tiles at a steady rate
        def pace(timestamp):
            """
            Send the next tile of the current phase

            N.B.: this is an alarm handler; it hands back the time until its next call, or
            {None} once the tiles of the second phase have all been sent
            """
            # the tiles of the current phase
            queue = queues[state["phase"]]
            # if there is one left
            if queue:
                # send it
                submit(origin=queue.popleft(), phase=state["phase"])
            # the second phase ends when its tiles have all been sent
            if state["phase"] == "after" and not queue:
                # so stop pacing
                return None
            # otherwise, keep going
            return interval * second

        # the end of the run
        def settle():
            """
            Stop the loop once the build is over and every tile of the second phase is back
            """
            # if that is the case
            if state["phase"] == "after" and not queues["after"] and state["flight"] == 0:
                # the run is over
                fleet.dispatcher.stop()
            # all done
            return

        # send a tile to the crew
        def submit(origin, phase):
            """
            Send the tile at {origin} to the crew, as part of {phase}
            """
            # describe it the way the server does
            task = qed.nexus.tile(
                view=view,
                channel=f"{dataset.pyre_name}.{name}",
                zoom=(zoom, zoom),
                origin=origin,
                shape=(span, span),
                workspace=workspace,
            )
            # note when it left
            start = clock.sec()

            # when it comes back
            def delivered(result=None, error=None):
                """
                Record the tile, and end the run if it was the last one
                """
                # record it
                records.append((phase, start, (clock.sec() - start) * 1000, error is not None))
                # it is no longer in flight
                state["flight"] -= 1
                # and the run may be over
                settle()
                # all done
                return

            # it is in flight
            state["flight"] += 1
            # send it
            fleet.render(task=task, callback=delivered)
            # all done
            return

        # when the dataset is worth looking at
        def seeded(build):
            """
            The first tiles of the dataset have reported
            """
            # note when
            state["seeded"] = clock.sec()
            # all done
            return

        # when a build is over
        def over(build, error=None):
            """
            A build is done, or failed with {error}; once they all are, the second phase starts
            """
            # a failure
            if error is not None:
                # has its reason noted
                errors.append(str(error))
            # once every build is over
            if all(build.done for build in builds):
                # note when
                state["ready"] = clock.sec()
                # switch to the second phase; the pacer takes it from here
                state["phase"] = "after"
                # unless there is nothing left to wait for
                settle()
            # all done
            return

        # when the run takes too long
        def overdue(timestamp):
            """
            The run has taken longer than its patience allows

            N.B.: this is an alarm handler; returning {None} keeps it from being rescheduled
            """
            # note it
            errors.append(f"gave up after {self._buildPatience} s")
            # and stop the loop
            fleet.dispatcher.stop()
            # the alarm is done
            return None

        # the rasters: the dataset, and the ones it is read with, since a masked render reads
        # all of them at one depth or none of them
        rasters = [dataset] + list(dataset.companions().values())
        # go through them
        for raster in rasters:
            # the pyramid, laid out in the workspace
            pyramid = qed.readers.nisar.pyramid(reader=reader, dataset=raster, workspace=workspace)
            # and its build; only the dataset reports its seed, as it does in the server
            builds.append(
                qed.nexus.build(
                    reader=reader,
                    dataset=raster,
                    pyramid=pyramid,
                    fleet=fleet,
                    statistics=qed.ux.sample(),
                    onSeeded=seeded if raster is dataset else None,
                    onDone=over,
                    onFailed=over,
                )
            )
        # start the clock
        clock.reset()
        clock.start()
        # start the builds
        for build in builds:
            # each hands out its first level
            build.start()
        # and the tiles, which join the workplan behind the first level
        fleet.dispatcher.alarm(interval=interval * second, call=pace)
        # give up if the run takes too long
        fleet.dispatcher.alarm(interval=self._buildPatience * second, call=overdue)
        # run the loop until the run is over
        fleet.dispatcher.watch()
        # stop the clock
        clock.stop()
        # let the crew go
        fleet.disband()
        # the state the builds ended in
        status = "; ".join(errors) if errors else "ready"
        # hand off the times, the state, and the tiles
        return state["seeded"], state["ready"], status, records

    # implementation details: the caches
    def _cacheRun(self, plexus, pattern, buffer, budget):
        """
        Read a block of chunks of the dataset at my {location} in the access {pattern}, through
        a page buffer of {buffer} MiB and a chunk cache of {budget} MiB, and record what it cost
        """
        # make a channel
        channel = journal.info("qed.measure.caches")
        # the host label that lets records from different machines share a file
        host = self.pyre_host.nickname
        # the records land next to the others
        stem = os.path.splitext(self.output)[0]
        # the store is the authority on the connected data sources
        ux = plexus._ux
        # find the reader the sweep named, without opening it
        reader = next(
            (
                source
                for source in (ux.store.sources if ux else [])
                if source.pyre_name in self.only
            ),
            None,
        )
        # if it is not there
        if reader is None:
            # complain
            error = journal.error("qed.measure.caches")
            error.log(f"no reader among {', '.join(self.only)}")
            # and bail
            return 1
        # the access list of the file, with the page buffer under measurement; the shares of
        # metadata and raw data are those of the NISAR readers
        fapl = qed.h5.libh5.properties.fapl()
        # a page buffer, when asked for
        if buffer:
            # gets its size
            fapl.pageBufferSize = qed.h5.libh5.properties.PageBuffer(
                bytes=buffer * 2**20, metadata=5, raw=50
            )
        # the access list of the dataset, with the chunk cache under measurement
        dapl = qed.h5.libh5.properties.dapl()
        # a chunk cache, when asked for
        if budget:
            # gets its size; the index gets many more slots than the cache holds chunks, a prime
            # number of them, the way the library recommends
            dapl.chunkCache = qed.h5.libh5.properties.ChunkCache(
                slots=100003, bytes=budget * 2**20, preemption=0.75
            )
        # before the file is opened, measure the process
        before = self._resident()
        # open the file with the credentials of the reader, before the reader does, since the
        # opens that follow share the caches of the first
        h5 = qed.h5.reader(uri=reader.uri, credentials=reader.grant(), fapl=fapl)
        # get the file itself
        file = h5._file._pyre_id
        # and the dataset, through its access list
        h5ds = file.dataset(self.location, dapl)
        # once it is open, measure the process again
        opened = self._resident()
        # now the reader can make first contact; the layout is metadata, so nothing is sampled
        reader.open(measure=False)
        # find the dataset the sweep named
        dataset = next(
            (entry for entry in reader.datasets if entry.pyre_name in self.rasters), None
        )
        # if it is not there
        if dataset is None:
            # complain
            error = journal.error("qed.measure.caches")
            error.log(f"'{reader.pyre_name}' has no dataset among {', '.join(self.rasters)}")
            # and bail
            return 1
        # the layout of the file, which the sweep checked is HDF5
        pageSize, _, _ = qed.readers.pages.paging(reader=reader)
        # the chunk table of the dataset, as (address, bytes, origin)
        table = qed.readers.pages.tables(reader=reader)[dataset.pyre_name]
        # the shape of a chunk
        tile = tuple(dataset.tile)
        # the size of a chunk before the filters
        raw = tile[0] * tile[1] * dataset.data.disktype.bytes
        # what the dataset holds where there is nothing
        fill = qed.readers.pages.nodata(dataset=dataset, table=table, raw=raw)
        # the stored size of a chunk of fill, when there are such chunks
        empty = min(size for _, size, _ in table) if fill["fillChunks"] else None
        # the chunks that hold data, by origin
        chunks = {origin: (address, size) for address, size, origin in table if size != empty}
        # find a block of them
        side, corner = self._solid(chunks=chunks, tile=tile, side=self.block)
        # if there is none
        if corner is None:
            # complain
            error = journal.error("qed.measure.caches")
            error.log(f"'{dataset.pyre_name}' has no block of chunks that all hold data")
            # and bail
            return 1
        # the origins of the chunks of the block, in raster order
        origins = [
            (corner[0] + i * tile[0], corner[1] + j * tile[1])
            for i in range(side)
            for j in range(side)
        ]
        # the pages they occupy
        pages = {chunks[origin][0] // pageSize for origin in origins} if pageSize else set()
        # the bytes they store
        stored = sum(chunks[origin][1] for origin in origins)
        # start the tally of the page buffer over, so the survey of the layout is not counted
        file.resetPageBuffer()
        # and measure the process right before the passes
        ready = self._resident()
        # the type of its cells, as they are stored, so that nothing is converted
        memtype = dataset.data.disktype
        # a buffer for a chunk
        data = bytearray(raw)
        # the passes of the pattern: a stream reads every chunk once, in the order of their
        # addresses; a revisit reads them in raster order, twice
        if pattern == "stream":
            # one pass, in the order of their addresses
            passes = [sorted(origins, key=lambda origin: chunks[origin][0])]
        # otherwise
        else:
            # two passes in raster order
            passes = [origins, origins]
        # the clocks
        wallclock = qed.timers.wall("qed.measure.caches.wall")
        cpuclock = qed.timers.cpu("qed.measure.caches.cpu")
        # open the file of records for appending
        with self._records(path=f"{stem}-caches.csv", headers=self._cacheHeaders) as out:
            # go through the passes
            for index, order in enumerate(passes):
                # start the tally of the page buffer over, when there is one
                file.resetPageBuffer()
                # start both clocks afresh
                wallclock.reset()
                cpuclock.reset()
                wallclock.start()
                cpuclock.start()
                # read the chunks
                for origin in order:
                    # one at a time
                    h5ds.read(data=data, memtype=memtype, origin=origin, shape=tile)
                # stop the clocks
                wallclock.stop()
                cpuclock.stop()
                # what the page buffer saw, if there is one, as (metadata, raw data)
                seen = file.pageBuffer
                # the page activity of the raw data
                accesses, hits, misses = (
                    (seen.accesses[1], seen.hits[1], seen.misses[1]) if seen else (0, 0, 0)
                )
                # the process, after the pass
                after = self._resident()
                # record the pass
                out.writerow(
                    (
                        host,
                        dataset.pyre_name,
                        pattern,
                        buffer,
                        budget,
                        side,
                        len(origins),
                        len(pages),
                        stored,
                        index + 1,
                        f"{wallclock.ms():.3f}",
                        f"{cpuclock.ms():.3f}",
                        accesses,
                        hits,
                        misses,
                        (opened - before) // 2**20,
                        (after - ready) // 2**20,
                    )
                )
                # and report it
                channel.line(
                    f"{dataset.pyre_name}: {pattern} pass {index + 1}, "
                    f"page buffer {buffer} MiB, chunk cache {budget or 'default'} MiB: "
                    f"{len(origins)} chunks on {len(pages)} pages, "
                    f"{wallclock.ms():.1f} ms wall, {cpuclock.ms():.1f} ms cpu, "
                    f"page misses {misses} of {accesses}, "
                    f"{(after - ready) / 2**20:.0f} MiB more resident than before the passes"
                )
        # flush the report
        channel.log()
        # all done
        return 0

    def _solid(self, chunks, tile, side):
        """
        Find the corner of a block of {side} by {side} {chunks} that all hold data, as near the
        center of their extent as possible, shrinking the block when there is no such block;
        hand back the side of the block that was found, and its corner, or {None}
        """
        # the extent of the chunks that hold data
        rows = [origin[0] for origin in chunks]
        cols = [origin[1] for origin in chunks]
        # and its center
        center = ((min(rows) + max(rows)) / 2, (min(cols) + max(cols)) / 2)
        # the candidate corners, nearest the center first
        corners = sorted(chunks, key=lambda o: (o[0] - center[0]) ** 2 + (o[1] - center[1]) ** 2)
        # try blocks of decreasing size
        for size in range(side, 0, -1):
            # go through the candidates
            for row, col in corners:
                # a block whose every chunk holds data
                if all(
                    (row + i * tile[0], col + j * tile[1]) in chunks
                    for i in range(size)
                    for j in range(size)
                ):
                    # is the one
                    return size, (row, col)
        # nothing holds data
        return 0, None

    def _resident(self):
        """
        Measure the resident memory of this process, in bytes
        """
        # on linux, the kernel publishes it
        if os.path.exists("/proc/self/statm"):
            # as a number of pages, the second entry of the record
            with open("/proc/self/statm") as stream:
                # so read it
                pages = int(stream.read().split()[1])
            # and convert
            return pages * os.sysconf("SC_PAGE_SIZE")
        # elsewhere, ask the process table, which reports KiB
        kib = subprocess.check_output(["ps", "-o", "rss=", "-p", str(os.getpid())])
        # and convert
        return int(kib) * 1024

    # implementation details: the census
    def _scraped(self, channel, prefix, product):
        """
        Choose the granules of {product} in my {cycle} from my {scrape}, as (granule, key), all
        of them or my {quota} spread evenly over the cycle, and report the parse to {channel}
        """
        # the parser of the granule ids
        registrar = qed.readers.nisar.daac.registrar()
        # the clock of the parse
        clock = qed.timers.wall(f"qed.measure.census.parse.{product}")
        # started afresh
        clock.reset()
        clock.start()
        # the number of ids in the list
        ids = 0
        # the granules of the cycle, as (mark, granule, key)
        found = []
        # and the number of ids the parser did not recognize
        unrecognized = 0
        # go through the list
        with open(self.scrape / f"{product}.txt") as stream:
            # one granule id per line
            for line in stream:
                # clean it up
                granule = line.strip()
                # skip blank lines
                if not granule:
                    # by moving on
                    continue
                # count the id
                ids += 1
                # sift it by its raw fields, which is cheap
                fields = registrar.fields(granule)
                # an id the parser does not recognize
                if fields is None:
                    # is counted
                    unrecognized += 1
                    # and skipped
                    continue
                # the cycle, which for a pair is the one of its reference acquisition
                cycle = fields.get("cycle") or fields.get("referenceCycle")
                # a granule of another cycle
                if int(cycle) != self.cycle:
                    # is not wanted
                    continue
                # the ones that are get a descriptor
                descriptor = registrar.parse(granule)
                # and the key of their product in the canonical layout of the bucket
                key = qed.readers.nisar.daac.canonical(prefix=prefix, descriptor=descriptor)
                # add it to the pile, with the time that orders it
                found.append((descriptor.mark, granule, key))
        # stop the clock of the parse
        clock.stop()
        # and report it
        channel.log(
            f"{product}: parsed {ids} ids in {clock.sec():.1f} s; {len(found)} in cycle "
            f"{self.cycle}; {unrecognized} of all the ids in the list not recognized"
        )
        # in the order they were acquired
        found.sort()
        # a quota picks that many, spread evenly over the cycle
        if self.quota is not None and 1 < self.quota < len(found):
            # by striding through the pile
            found = [
                found[round(i * (len(found) - 1) / (self.quota - 1))] for i in range(self.quota)
            ]
        # a quota of one takes the one in the middle
        elif self.quota == 1 and found:
            # of the pile
            found = [found[len(found) // 2]]
        # hand off the granules and their keys
        return [(granule, key) for _, granule, key in found]

    def _missing(self, uri):
        """
        Decide whether the product at {uri} could not be opened because it is not there; only a
        product in a bucket can tell, by asking the bucket
        """
        # normalize the location
        uri = qed.primitives.uri.parse(value=str(uri), scheme="file")
        # a product that is not in a bucket
        if uri.scheme != "s3":
            # has no bucket to ask
            return False
        # the bucket is asked through the AWS client, which qed does not require
        try:
            # so look for it
            import boto3
            import botocore.exceptions
        # without it
        except ImportError:
            # there is no way to tell
            return False
        # the bucket and the key
        bucket, _, key = f"{uri.authority}{uri.address}".partition("/")
        # attempt to
        try:
            # look the product up, with the credentials of the standard AWS chain
            boto3.client("s3").head_object(Bucket=bucket, Key=key)
        # if the bucket said no
        except botocore.exceptions.ClientError as error:
            # it is missing if the bucket says it is not there, and anything else is a failure
            return error.response.get("Error", {}).get("Code") in ("404", "NoSuchKey", "NotFound")
        # otherwise, it is there, so it failed to open for some other reason
        return False

    def _survey(self, channel, results, bucket, jobs):
        """
        Measure the granules in {jobs}, my {workers} of them at a time, each in a fresh process
        whose output the event loop collects into its log, and hand off the ones that did not
        complete and the ones whose product is not there
        """
        # the journal channel that reports the progress, since the handlers of the event loop
        # are handed the channel they watch under the same name
        reporter = channel
        # the event loop that watches the measurements
        selector = pyre.ipc.newSelector(name="qed.measure.census")
        # the granules still to measure
        pending = collections.deque(jobs)
        # the measurements under way
        running = set()
        # the ones that did not complete
        failures = []
        # and the ones whose product is not there
        absent = []

        # start as many measurements as there is room for
        def launch():
            """
            Start the next measurements, until my {workers} are busy or nothing is pending
            """
            # while there is room and work
            while pending and len(running) < self.workers:
                # take the next granule
                kind, granule, key = pending.popleft()
                # start measuring it
                process, log = self._census(
                    results=results, bucket=bucket, kind=kind, granule=granule, key=key
                )
                # it is under way
                running.add(process)
                # wrap its output, so the event loop can watch it
                output = Pipe(infd=process.stdout.fileno(), outfd=process.stdout.fileno())
                # collect what it says, and learn from the end of it that it is done
                selector.whenReadReady(
                    channel=output,
                    call=functools.partial(
                        collect, process=process, log=log, kind=kind, granule=granule
                    ),
                )
                # and give up on it if it takes too long
                selector.alarm(
                    interval=self._patience * second,
                    call=functools.partial(overdue, process=process, log=log),
                )
            # all done
            return

        # collect the output of a measurement
        def collect(channel, process, log, kind, granule, **kwds):
            """
            Add what the measurement of {granule} says to its {log}, and settle it once it is
            done
            """
            # read what it said
            chunk = os.read(channel.inbound, 1 << 16)
            # if it said something
            if chunk:
                # keep it
                log.write(chunk)
                # and keep listening
                return True
            # otherwise, it is done talking; let go of its output
            process.stdout.close()
            # collect its exit status
            status = process.wait()
            # close its log
            log.close()
            # it is no longer under way
            running.discard(process)
            # if its product is not there
            if status == self._absent:
                # remember it
                absent.append(f"{kind} {granule}")
                # and say so
                message = f"{kind} {granule}: no product"
            # if it failed
            elif status != 0:
                # remember it for the summary
                failures.append(f"{kind} {granule}")
                # and say so
                message = f"{kind} {granule}: failed with status {status}"
            # otherwise
            else:
                # say it is done
                message = f"{kind} {granule}: measured"
            # report it
            reporter.log(message)
            # start the next ones
            launch()
            # if nothing is under way, nothing is left
            if not running:
                # so the census is over
                selector.stop()
            # stop listening to this one
            return False

        # the deadline of a measurement
        def overdue(timestamp, process, log):
            """
            The measurement behind {process} has taken too long

            N.B.: this is an alarm handler; returning {None} keeps it from being rescheduled
            """
            # a measurement that is still running
            if process.poll() is None:
                # leaves a note in its log
                log.write(f"census: gave up after {self._patience} seconds\n".encode("utf-8"))
                # and is stopped; its output closes, which settles it
                process.kill()
            # the alarm is done
            return None

        # start the first ones
        launch()
        # if anything is under way
        if running:
            # watch until the last one is done
            selector.watch()
        # hand off the ones that did not complete, and the ones whose product is not there
        return failures, absent

    def _census(self, results, bucket, kind, granule, key):
        """
        Start measuring the page layout of the {granule} of the product {kind}, named after its
        reader, at {key} in {bucket} in a fresh process, from a folder of its own under
        {results}, and hand off the process and the log that collects its output
        """
        # the folder of the granule
        directory = results / kind / granule
        # make it
        directory.mkdir(parents=True)
        # write the configuration the measurement reads
        self._configure(directory=directory, uri=f"s3://{bucket}/{key}", flavor=kind)
        # open the log that collects its output
        log = open(directory / "pages.log", mode="wb")
        # launch the measurement, with its output on a pipe the event loop watches
        process = subprocess.Popen(
            [
                "qed",
                "--shell=script",
                "measure",
                "pages",
                "--only=product",
                "--compress=yes",
                f"--output={directory / 'layout.csv'}",
            ],
            cwd=directory,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        # hand off the process and its log
        return process, log

    def _gather(self, results, jobs):
        """
        Collect the summaries of every dataset of the granules in {jobs} into one table in
        {results}, and hand them off as records
        """
        # the columns: the granule, then its dataset summaries
        headers = ("kind", "granule", "crid") + self._occupancyHeaders
        # the records
        rows = []
        # open the table
        with open(results / "census.csv", mode="w", newline="") as stream:
            # make a writer
            writer = csv.writer(stream)
            # write the header
            writer.writerow(headers)
            # go through the granules
            for kind, granule, _ in jobs:
                # the summaries of its datasets
                path = results / kind / granule / "layout-occupancy.csv"
                # a granule whose measurement did not complete has none
                if not path.exists():
                    # so skip it
                    continue
                # the processing version is the last token of the name of six characters, a
                # letter and five digits
                crid = [
                    token
                    for token in granule.split("_")
                    if len(token) == 6 and token[0].isalpha() and token[1:].isdigit()
                ]
                # read the summaries
                with open(path, newline="") as source:
                    # one dataset at a time
                    for record in csv.DictReader(source):
                        # tag it with its granule
                        row = {
                            "kind": kind,
                            "granule": granule,
                            "crid": crid[-1] if crid else "",
                            **record,
                        }
                        # write it
                        writer.writerow(row[header] for header in headers)
                        # and keep it
                        rows.append(row)
        # hand off the records
        return rows

    def _tally(self, channel, rows):
        """
        Report the census {rows} by kind of product: the medians over the datasets of the
        amplification, the fill of the pages, the nearly empty chunks, and the locality
        """
        # the records, by kind
        kinds = {}
        # go through them
        for row in rows:
            # and file each one
            kinds.setdefault(row["kind"], []).append(row)
        # go through the kinds
        for kind, records in kinds.items():
            # the numbers of a column, leaving out the datasets that have none
            def column(name):
                # convert what is there
                return [float(record[name]) for record in records if record[name] != ""]

            # the median of a column, or {None} when nothing has it
            def median(name):
                # get the numbers
                values = column(name)
                # and hand off their median, if there are any
                return statistics.median(values) if values else None

            # the share of the chunks of each dataset that are nearly empty
            empty = [
                float(record["empty"]) / float(record["written"])
                for record in records
                if float(record["written"])
            ]
            # the page sizes and strategies on offer
            layouts = sorted({(record["strategy"], record["page_size"]) for record in records})
            # sign on
            channel.line(
                f"{kind}: {len({record['granule'] for record in records})} granules, "
                f"{len(records)} datasets; "
                + ", ".join(
                    f"{strategy} strategy with pages of {int(size) / 2**20:g} MiB"
                    for strategy, size in layouts
                )
            )
            # the medians over the datasets
            numbers = {
                "alone": median("alone"),
                "once": median("once"),
                "joint": median("joint"),
                "fill": median("fill_mean"),
                "total": median("total_mean"),
                "locality": median("locality"),
                "compression": median("compression"),
            }
            # render them, leaving out the ones nobody has
            channel.line(
                "  medians over the datasets: "
                + ", ".join(
                    f"{label} {value:.2f}" for label, value in numbers.items() if value is not None
                )
                + (f", nearly empty {statistics.median(empty):.0%}" if empty else "")
            )
        # all done
        return

    # private data
    # how long a tile of a swarm may take before it counts as a failure, in seconds; a small
    # team behind many clients over a remote product can keep a request waiting in line for
    # minutes, which is a result rather than a failure
    _tilePatience = 900
    # the exit status of a measurement of a product that is not there
    _absent = 3
    # how long the census waits for the measurement of one granule, in seconds
    _patience = 900
    # the most tiles the contention program lays out, which bounds how long it can keep asking
    # for tiles while a build runs
    _crowd = 100000
    # how long the pyramid measurement waits for a build, in seconds
    _buildPatience = 7200
    # how long the output of a measurement can pause before what it said counts as an entry
    _s3quiet = 0.2
    # the cells that hold data, by dataset, found on first use
    _anchors = None
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
        "workload",
    )
    # the column labels of the pyramid construction records
    _pyramidHeaders = (
        "host",
        "dataset",
        "channel",
        "team",
        "seeded_s",
        "ready_s",
        "status",
        "bytes",
    )
    # the column labels of the records of tiles during a build
    _contentionHeaders = (
        "host",
        "dataset",
        "channel",
        "team",
        "rate",
        "zoom",
        "span",
        "phase",
        "submitted_s",
        "latency_ms",
        "status",
        "seeded_s",
        "ready_s",
    )
    # the column labels of the cache records
    _cacheHeaders = (
        "host",
        "dataset",
        "pattern",
        "buffer_mib",
        "budget_mib",
        "side",
        "chunks",
        "pages",
        "stored",
        "pass",
        "wall_ms",
        "cpu_ms",
        "page_accesses",
        "page_hits",
        "page_misses",
        "open_mib",
        "resident_mib",
    )
    # the column labels of the per dataset page occupancy summaries
    _occupancyHeaders = (
        "host",
        "product",
        "dataset",
        "strategy",
        "page_size",
        "grid",
        "written",
        "stored",
        "raw",
        "compression",
        "empty",
        "pages",
        "alone",
        "once",
        "joint",
        "partners",
        "fill_median",
        "fill_mean",
        "fill_full",
        "total_mean",
        "tenants",
        "locality",
        "file_bytes",
        "rows",
        "cols",
        "tile_rows",
        "tile_cols",
        "cell",
        "filters",
        "size_histogram",
        "fill_histogram",
        "total_histogram",
        "empty_stored",
        "empty_pages",
        "hdf5_fill_status",
        "hdf5_fill",
        "cf_fill",
        "smallest_holds",
        "decode_s",
        "make_s",
        "data_decode_s",
        "fill_chunks",
        "fill_bytes",
        "fill_verified",
        "deflate_level",
        "encode_s",
    )
    # the column labels of the chunk layout records
    _pageHeaders = (
        "host",
        "dataset",
        "row",
        "col",
        "address",
        "bytes",
        "raw",
        "page_size",
        "first_page",
        "pages",
    )


# end of file
