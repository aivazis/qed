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
FLAVORS = ("rslc", "rifg", "runw", "roff", "gslc", "gunw", "gcov", "goff")


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
        "the directory that collects the results of the s3 program or the census; unset names "
        "one after the kind of run, the host, and the time"
    )

    # the census of the layout of the NISAR products in a bucket
    bucket = qed.properties.str()
    bucket.default = "s3://nisar-ops-rs-fwd/products/"
    bucket.doc = (
        "the prefix under which the census finds the NISAR products, laid out by kind, date, "
        "and granule"
    )

    kinds = qed.properties.strings()
    kinds.default = [
        "L1_L_RSLC",
        "L1_L_RIFG",
        "L1_L_RUNW",
        "L1_L_ROFF",
        "L2_L_GSLC",
        "L2_L_GUNW",
        "L2_L_GCOV",
        "L2_L_GOFF",
    ]
    kinds.doc = "the kinds of product the census measures, named the way the bucket names them"

    quota = qed.properties.int()
    quota.default = 24
    quota.doc = "the number of granules of each kind the census measures, spread over the dates"

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
            error.log("no dataset to measure; check the configuration and the restrictions")
            # and bail
            return 1
        # unpack the target
        reader, dataset, name, _ = first
        # the workload geometry: the smallest configured tile at the lowest configured zoom
        span = 2 ** self.shapes[0]
        zoom = self.zooms[0]
        # a warm swarm replays one workload at every level; a cold one needs a workload for
        # each level, so that no level is served tiles an earlier one already fetched
        batches = 1 if self.warm else len(self.clients)
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
        # launch the server
        process, log = self._launch(reader=reader)
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
            if self.warm:
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
        Build the pyramid of the first dataset the restrictions allow with a server of each of
        my {crews} sizes, from scratch every time, and record how long it takes until the view
        is worth looking at and until every level is built

        Each server works out of a folder of its own next to the measurement records, so no
        build finds the levels of an earlier one; once their size is on record the levels are
        removed, since a sweep would otherwise keep several copies of a pyramid that can be as
        large as the product, and the folder keeps the log of the server
        """
        # make a channel
        channel = journal.info("qed.measure.pyramid")
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
        # the configuration the servers read is the one in effect here
        configuration = os.path.join(os.getcwd(), "qed.yaml")
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
            # give it the configuration, if there is one
            if os.path.exists(configuration):
                # by copying it over
                shutil.copy(configuration, str(directory / "qed.yaml"))
            # build the pyramid and time it
            seeded, ready, status = self._build(
                reader=reader, dataset=dataset, name=name, team=team, directory=directory
            )
            # the bytes the levels occupy on disk; the levels are sized before any tile is
            # written, so the files are sparse and only the blocks that were written count
            size = sum(
                os.stat(os.path.join(root, entry)).st_blocks * 512
                for root, _, entries in os.walk(str(directory / ".qed"))
                for entry in entries
            )
            # the workspace of the server holds the levels, which have served their purpose
            workspace = directory / ".qed"
            # so if it is there
            if workspace.exists():
                # remove it
                shutil.rmtree(str(workspace))
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
        # go through them
        for reader, dataset in self._rasters(plexus=plexus):
            # and file each one with its reader
            readers.setdefault(reader, []).append(dataset)
        # open the file of per chunk records and the file of per dataset summaries, for
        # appending, so runs accumulate
        with (
            self._records(path=f"{stem}-pages.csv", headers=self._pageHeaders) as chunks,
            self._records(path=f"{stem}-occupancy.csv", headers=self._occupancyHeaders) as sums,
        ):
            # go through the readers
            for reader, datasets in readers.items():
                # the file layout is shared by all the datasets of a reader
                layout = self._layout(reader=reader)
                # a reader whose file is not HDF5 has no pages to speak of
                if layout is None:
                    # so say so
                    channel.line(f"{reader.pyre_name}: not an HDF5 product")
                    # and move on
                    continue
                # the chunk tables of every dataset in the file, since the datasets that share
                # the pages of the one being measured decide how much of each page it needs
                tables = self._chunks(reader=reader)
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
        Measure the page layout of {quota} granules of each of the {kinds} of NISAR product in
        {bucket}, spread over the dates on offer, and collect the summaries of every dataset in
        one table, so the structure of the products can be compared across kinds and dates

        Each granule is measured by {measure pages} in a fresh process, {workers} at a time;
        only metadata is read, so the census is cheap next to the data
        """
        # make a channel for the problems that stop the census before it starts
        error = journal.error("qed.measure.census")
        # every kind needs a reader
        unknown = [kind for kind in self.kinds if self._flavor(kind=kind) is None]
        # so a kind without one is a mistake
        if unknown:
            # say which
            error.log(f"no reader for {', '.join(unknown)}")
            # and bail
            return 1
        # the bucket has to be a bucket
        if not self.bucket.startswith("s3://"):
            # or else this is the wrong program
            error.log(f"'{self.bucket}' is not an s3 uri")
            # so bail
            return 1
        # the census lists the bucket through the AWS client, which qed does not require
        try:
            # so look for it
            import boto3
        # if it is not there
        except ImportError:
            # say so
            error.log("the census lists the bucket with 'boto3', which is not installed")
            # and bail
            return 1
        # the measurements run in child processes of the installed qed
        if shutil.which("qed") is None:
            # so it must be on the path
            error.log("there is no 'qed' on the path to run the measurements")
            # or there is nothing to measure with
            return 1
        # the directory that collects the results
        results = self._results(kind="census")
        # a directory that exists already would mix records from different runs
        if results.exists():
            # so refuse it
            error.log(f"'{results}' already exists")
            # and bail
            return 1
        # make it
        results.mkdir(parents=True)

        # make a channel for the progress of the census
        channel = journal.info("qed.measure.census")
        # which reaches the console and the run log alike
        channel.device = journal.tee(paths=[str(results / "run.log")])
        # say what is about to happen
        channel.line(f"on {self.pyre_host.nickname}")
        channel.line(f"{self.quota} granules of each of {', '.join(self.kinds)}")
        channel.line(f"from {self.bucket}")
        channel.line(f"results in {results}")
        # flush
        channel.log()
        # record the installation, so the numbers can be tied to the code that produced them
        self._about(channel=channel, results=results)

        # split the bucket from the prefix
        bucket, _, prefix = self.bucket.removeprefix("s3://").partition("/")
        # make a client, with the credentials of the standard AWS chain
        client = boto3.client("s3")
        # the granules to measure, as (kind, granule, key, bytes)
        jobs = []
        # go through the kinds
        for kind in self.kinds:
            # choose its granules
            chosen, skipped = self._choose(client=client, bucket=bucket, prefix=f"{prefix}{kind}/")
            # say how many there are, and how many folders held no product
            channel.line(f"{kind}: {len(chosen)} granules, {skipped} folders without a product")
            # and add them to the pile
            jobs.extend((kind, granule, key, size) for granule, key, size in chosen)
        # flush
        channel.log()

        # measure the granules, a few at a time, on the pyre event loop
        failures = self._survey(channel=channel, results=results, bucket=bucket, jobs=jobs)

        # gather the summaries into one table
        rows = self._gather(results=results, jobs=jobs)
        # and report them by kind
        self._tally(channel=channel, rows=rows)
        # list whatever did not complete, so a partial census is never mistaken for a whole
        for label in failures:
            # one per line
            channel.line(f"incomplete: {label}")
        # say it is over
        channel.line(f"done: {len(jobs) - len(failures)} of {len(jobs)} granules measured")
        # flush
        channel.log()
        # pack the results
        self._pack(channel=channel, results=results)
        # report failures through the exit status too
        return 1 if failures else 0

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
        ux = plexus._ux
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

    def _layout(self, reader):
        """
        Read the page size and the file space strategy of the file behind {reader}, or report
        that it is not an HDF5 product
        """
        # only the HDF5 readers have pages
        if not isinstance(reader, qed.readers.nisar.h5):
            # so everybody else has no layout
            return None
        # the file creation properties are only reachable through the file itself, so open it
        # again, with the same credentials; this reads nothing but metadata
        h5 = qed.h5.reader(uri=reader.uri, credentials=reader.grant())
        # get the creation properties
        fcpl = h5._file._pyre_id.fcpl
        # and the free space strategy among them
        strategy = fcpl.filespaceStrategy
        # hand off what matters
        return fcpl.pageSize, strategy.strategy.name

    @contextlib.contextmanager
    def _records(self, path, headers):
        """
        Open the file of records at {path} for appending, writing its {headers} on first
        contact, and hand off a writer
        """
        # check whether this is first contact
        fresh = not os.path.exists(path)
        # open the file for appending, so runs accumulate
        with open(path, mode="a", newline="") as stream:
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

    def _chunks(self, reader):
        """
        Read the chunk table of every dataset of {reader} as lists of (address, bytes, origin)
        """
        # the tables, by dataset name
        tables = {}
        # go through the datasets of the reader
        for dataset in reader.datasets:
            # and record the chunks that were written
            tables[dataset.pyre_name] = [
                (chunk.address, chunk.bytes, tuple(chunk.origin))
                for chunk in dataset.data.dataset.chunkTable()
            ]
        # hand off the tables
        return tables

    def _occupancy(self, channel, chunks, summaries, host, reader, dataset, layout, tables):
        """
        Record each chunk of {dataset} that was written, and report and summarize how its
        chunks sit on the pages of the file, alone and next to the datasets in {tables}
        """
        # unpack the layout
        pageSize, strategy = layout
        # unpack the extent and the tile
        rows, cols = tuple(dataset.shape)
        tileRows, tileCols = tuple(dataset.tile)
        # the size of a chunk before the filters had their way with it
        raw = tileRows * tileCols * dataset.data.disktype.bytes
        # the number of chunks the tiling describes
        grid = -(-rows // tileRows) * -(-cols // tileCols)
        # the name of the dataset
        name = dataset.pyre_name
        # go through its chunks
        for address, size, (row, col) in tables[name]:
            # the pages it spans, when the file has pages
            first = address // pageSize if pageSize else 0
            last = (address + size - 1) // pageSize if pageSize else 0
            # record it
            chunks.writerow(
                (host, name, row, col, address, size, raw, pageSize, first, last - first + 1)
            )
        # describe how it sits on the pages
        record = qed.readers.pages.occupancy(
            tables=tables,
            name=name,
            pageSize=pageSize,
            raw=raw,
            tile=(tileRows, tileCols),
            grid=grid,
        )
        # sign on
        channel.line(f"{name}:")
        channel.line(f"  file: {strategy} strategy, pages of {pageSize / 2**20:g} MiB")
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
            f"{qed.readers.pages.NEARLY_EMPTY:.0%} of their raw size"
        )
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
                summaries=summaries, host=host, reader=reader, strategy=strategy, record=record
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
            summaries=summaries, host=host, reader=reader, strategy=strategy, record=record
        )
        # all done
        return

    def _summarize(self, summaries, host, reader, strategy, record):
        """
        Add the summary {record} of a dataset of {reader} to the file of {summaries}
        """
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

    def _launch(self, reader, team=None, levels=None, directory=None, path=None):
        """
        Launch the installed qed server with the swarm configuration, with a crew of {team}
        workers, or my {team}, building {levels}, or not, as my {levels} say, from
        {directory}, or from here, logging to {path}, or next to the measurement records
        """
        # the size of the crew
        team = self.team if team is None else team
        # whether it builds levels
        levels = self.levels if levels is None else levels
        # the server output lands next to the measurement records, unless told otherwise
        path = f"{os.path.splitext(self.output)[0]}-server.log" if path is None else path
        # open its log
        log = open(path, mode="w")
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
            f"--qed.app.nexus.services.web.fleet.{reader.pyre_name}.size={team}",
            # building the levels of the product, unless asked not to
            f"--qed.app.pyramids={'yes' if levels else 'no'}",
        ]
        # launch, from the directory whose configuration and workspace the server uses
        process = subprocess.Popen(
            cmd, cwd=directory, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT
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
    def _build(self, reader, dataset, name, team, directory):
        """
        Launch a server with a crew of {team} from {directory}, select the {dataset} of {reader}
        through the channel {name}, and time the construction of its pyramid, as the seconds
        until it is seeded, the seconds until it is ready, and the state it ended in
        """
        # launch the server, building levels, with its log in the folder of the build
        process, log = self._launch(
            reader=reader,
            team=team,
            levels=True,
            directory=str(directory),
            path=str(directory / "server.log"),
        )
        # the times, unknown until they happen
        seeded = None
        ready = None
        # and the state the build ends in
        status = "unknown"
        # from here on, the server must come down no matter what happens
        try:
            # wait for it to accept connections
            if not self._ready():
                # if it never came up, say so
                return seeded, ready, "no server"
            # make first contact before the clock starts, so the time is the build's alone
            self._stage()
            # selecting the dataset is what starts the build, so the clock starts here
            clock = qed.timers.wall(f"qed.measure.pyramid.team{team}")
            # afresh
            clock.reset()
            clock.start()
            # drive the selections the way the client would
            self._select(reader=reader, dataset=dataset, channel=name)
            # watch the preparation, but not forever
            while clock.sec() < self._buildPatience:
                # ask the server how it is going
                reply = self._graphql(query="{ qed { views { preparation } } }")
                # the state of the view i drove
                status = reply["data"]["qed"]["views"][0]["preparation"] or "none"
                # the time so far
                elapsed = clock.sec()
                # a seeded build, or one that got past it, has been seeded
                if seeded is None and status in ("seeded", "ready"):
                    # so note when
                    seeded = elapsed
                # a build that is done
                if status == "ready":
                    # is done
                    ready = elapsed
                    # so stop watching
                    break
                # a build that failed, or a dataset nobody is preparing, will not get better
                if status in ("failed", "none"):
                    # so stop watching
                    break
                # otherwise, wait a beat
                time.sleep(self._buildBeat)
            # if the watch ran out
            else:
                # say so
                status = f"{status}, gave up after {self._buildPatience} s"
            # the build is over, one way or another
            clock.stop()
        # no matter how the build went
        finally:
            # bring the server down
            self._stop(process=process, log=log)
        # hand off the times and the state
        return seeded, ready, status

    # implementation details: the census
    def _flavor(self, kind):
        """
        The reader of the products of {kind}, named the way the bucket names them, or {None}
        """
        # the kind of product is the last part of the name
        flavor = kind.rsplit("_", 1)[-1].lower()
        # hand it off, if there is a reader for it
        return flavor if flavor in FLAVORS else None

    def _folders(self, client, bucket, prefix):
        """
        List the folders directly under {prefix} in {bucket}, in order
        """
        # the folders
        folders = []
        # the listing comes in pages
        pages = client.get_paginator("list_objects_v2")
        # go through them
        for page in pages.paginate(Bucket=bucket, Prefix=prefix, Delimiter="/"):
            # and collect the folders of each
            folders.extend(entry["Prefix"] for entry in page.get("CommonPrefixes", []))
        # hand them off, in order
        return sorted(folders)

    def _choose(self, client, bucket, prefix):
        """
        Choose my {quota} of granules under {prefix}, spread evenly over the dates on offer, as
        (granule, key, bytes), and count the folders passed over because they hold no product
        """
        # the dates on offer, as their folders
        days = [prefix]
        # the layout goes year, month, and day
        for _ in range(3):
            # so descend one level at a time
            days = [
                folder
                for parent in days
                for folder in self._folders(client=client, bucket=bucket, prefix=parent)
            ]
        # the number of days to draw from
        count = min(self.quota, len(days))
        # with nothing to draw from, or nothing to draw
        if count < 1:
            # there is nothing to choose, and nothing passed over
            return [], 0
        # spread the days evenly over the ones on offer
        picks = (
            [days[round(i * (len(days) - 1) / (count - 1))] for i in range(count)]
            if count > 1
            else [days[len(days) // 2]]
        )
        # the granule folders of each chosen day, to draw from one at a time
        pools = [iter(self._folders(client=client, bucket=bucket, prefix=day)) for day in picks]
        # the granules chosen
        granules = []
        # and the folders passed over because they hold no product
        skipped = 0
        # draw one granule from each day in turn, until the quota is met or the days run dry
        while len(granules) < self.quota and pools:
            # go through the days that still have folders
            for pool in list(pools):
                # once the quota is met
                if len(granules) >= self.quota:
                    # there is nothing more to draw
                    break
                # look through the folders of this day
                for folder in pool:
                    # for one that holds its product
                    found = self._product(client=client, bucket=bucket, folder=folder)
                    # if this one does
                    if found is not None:
                        # choose it
                        granules.append(found)
                        # and move on to the next day
                        break
                    # otherwise, pass it over
                    skipped += 1
                # a day whose folders ran out
                else:
                    # has nothing more to offer
                    pools.remove(pool)
        # hand off the granules, and the number of folders passed over
        return granules, skipped

    def _product(self, client, bucket, folder):
        """
        Look up the product file of the granule in {folder} of {bucket}, as (granule, key,
        bytes), or {None} if the folder holds only its metadata
        """
        # the errors of the AWS client
        import botocore.exceptions

        # the granule is named after its folder
        granule = folder.rstrip("/").rsplit("/", 1)[-1]
        # and so is its product file
        key = f"{folder}{granule}.h5"
        # attempt to
        try:
            # look it up
            head = client.head_object(Bucket=bucket, Key=key)
        # if it is not there
        except botocore.exceptions.ClientError:
            # the folder has no product
            return None
        # otherwise, hand off the granule, with the size of its product
        return granule, key, head["ContentLength"]

    def _survey(self, channel, results, bucket, jobs):
        """
        Measure the granules in {jobs}, my {workers} of them at a time, each in a fresh process
        whose output the event loop collects into its log, and hand off the ones that did not
        complete
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
        # and the ones that did not complete
        failures = []

        # start as many measurements as there is room for
        def launch():
            """
            Start the next measurements, until my {workers} are busy or nothing is pending
            """
            # while there is room and work
            while pending and len(running) < self.workers:
                # take the next granule
                kind, granule, key, _ = pending.popleft()
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
            # if it failed
            if status != 0:
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
        # hand off the ones that did not complete
        return failures

    def _census(self, results, bucket, kind, granule, key):
        """
        Start measuring the page layout of the {granule} of {kind} at {key} in {bucket} in a
        fresh process, from a folder of its own under {results}, and hand off the process and
        the log that collects its output
        """
        # the folder of the granule
        directory = results / kind / granule
        # make it
        directory.mkdir(parents=True)
        # write the configuration the measurement reads
        self._configure(
            directory=directory, uri=f"s3://{bucket}/{key}", flavor=self._flavor(kind=kind)
        )
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
        headers = ("kind", "granule", "bytes", "crid") + self._occupancyHeaders
        # the records
        rows = []
        # open the table
        with open(results / "census.csv", mode="w", newline="") as stream:
            # make a writer
            writer = csv.writer(stream)
            # write the header
            writer.writerow(headers)
            # go through the granules
            for kind, granule, _, size in jobs:
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
                            "bytes": size,
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
    # how long the census waits for the measurement of one granule, in seconds
    _patience = 900
    # how long the pyramid measurement waits for a build, and how often it looks, in seconds
    _buildPatience = 7200
    _buildBeat = 0.5
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
