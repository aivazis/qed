# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import concurrent.futures
import csv
import journal
import json
import math
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
        # the per chunk records land next to the others
        stem = os.path.splitext(self.output)[0]
        # in their own file
        path = f"{stem}-pages.csv"
        # check whether this is first contact
        fresh = not os.path.exists(path)
        # open the file for appending, so runs accumulate
        with open(path, mode="a", newline="") as stream:
            # make a writer
            writer = csv.writer(stream)
            # on first contact
            if fresh:
                # write the header
                writer.writerow(self._pageHeaders)
            # go through the datasets the restrictions allow
            for reader, dataset in self._rasters(plexus=plexus):
                # the file layout is shared by all the datasets of a reader
                layout = self._layout(reader=reader)
                # a reader whose file is not HDF5 has no pages to speak of
                if layout is None:
                    # so say so
                    channel.line(f"{dataset.pyre_name}: not an HDF5 product")
                    # and move on
                    continue
                # measure this one
                self._occupancy(
                    channel=channel,
                    writer=writer,
                    host=host,
                    dataset=dataset,
                    layout=layout,
                )
        # flush the report
        channel.log()
        # all done
        return 0

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

    def _occupancy(self, channel, writer, host, dataset, layout):
        """
        Walk the chunk grid of {dataset}, record each chunk that was written, and report how
        the chunks sit on the pages of the file
        """
        # unpack the layout
        pageSize, strategy = layout
        # get the low level dataset
        h5 = dataset.data.dataset
        # unpack the extent and the tile
        rows, cols = tuple(dataset.shape)
        tileRows, tileCols = tuple(dataset.tile)
        # the size of a chunk before the filters had their way with it
        raw = tileRows * tileCols * dataset.data.disktype.bytes
        # the number of chunks the tiling describes
        grid = -(-rows // tileRows) * -(-cols // tileCols)
        # the chunks that were written, as (address, bytes)
        chunks = []
        # go through them
        for chunk in h5.chunkTable():
            # the pages it spans, when the file has pages
            first = chunk.address // pageSize if pageSize else 0
            last = (chunk.address + chunk.bytes - 1) // pageSize if pageSize else 0
            # unpack its corner
            row, col = chunk.origin
            # record it
            writer.writerow(
                (
                    host,
                    dataset.pyre_name,
                    row,
                    col,
                    chunk.address,
                    chunk.bytes,
                    raw,
                    pageSize,
                    first,
                    last - first + 1,
                )
            )
            # and remember it
            chunks.append((chunk.address, chunk.bytes))
        # sign on
        channel.line(f"{dataset.pyre_name}:")
        channel.line(f"  file: {strategy} strategy, pages of {pageSize / 2**20:g} MiB")
        # if nothing was written
        if not chunks:
            # there is nothing else to say
            channel.line(f"  none of its {grid} chunks were written")
            # so bail
            return
        # the stored sizes, in order
        sizes = sorted(size for _, size in chunks)
        # their total
        stored = sum(sizes)
        # report the chunk table
        channel.line(
            f"  chunks: {len(chunks)} of {grid} written ({len(chunks) / grid:.0%}), "
            f"{stored / 2**20:.1f} MiB stored"
        )
        # and the sizes, against the raw chunk
        channel.line(
            f"  chunk size: raw {raw / 2**20:.2f} MiB; stored median "
            f"{sizes[len(sizes) // 2] / 2**20:.2f} MiB, from {sizes[0] / 2**10:.1f} KiB "
            f"to {sizes[-1] / 2**20:.2f} MiB; compression {raw * len(sizes) / stored:.2f}x"
        )
        # a file without pages is read in byte ranges, so the rest does not apply
        if not pageSize:
            # say so
            channel.line("  the file is not paged; a reader fetches each chunk as one range")
            # and bail
            return
        # the bytes of this dataset on each page, and the chunks that touch it
        fill = {}
        tenants = {}
        # the number of pages each chunk spans
        spans = []
        # go through the chunks
        for address, size in chunks:
            # the pages it lands on
            first = address // pageSize
            last = (address + size - 1) // pageSize
            # remember the span
            spans.append(last - first + 1)
            # and apportion its bytes among them
            for page in range(first, last + 1):
                # the part of the chunk that falls on this page
                start = max(address, page * pageSize)
                end = min(address + size, (page + 1) * pageSize)
                # adds to its fill
                fill[page] = fill.get(page, 0) + end - start
                # and the chunk is one of its tenants
                tenants[page] = tenants.get(page, 0) + 1
        # tally the spans
        histogram = {}
        # by number of pages
        for span in spans:
            # lumping everything past three together
            key = span if span < 3 else 3
            # count it
            histogram[key] = histogram.get(key, 0) + 1
        # report them
        channel.line(
            "  pages per chunk: "
            + ", ".join(
                f"{'3+' if key == 3 else key}: {count} ({count / len(spans):.0%})"
                for key, count in sorted(histogram.items())
            )
        )
        # the bytes a reader that fetches whole pages moves to read each chunk on its own
        alone = sum(spans) * pageSize
        # and the bytes it moves to read them all, with every page fetched once
        together = len(fill) * pageSize
        # report the amplification of both
        channel.line(
            f"  read amplification: {alone / stored:.2f}x reading one chunk at a time, "
            f"{together / stored:.2f}x reading every chunk with each page fetched once"
        )
        # the occupancy of the pages that hold any of this dataset
        occupancy = sorted(size / pageSize for size in fill.values())
        # report it
        channel.line(
            f"  pages: {len(fill)} hold part of it; the dataset fills a median of "
            f"{occupancy[len(occupancy) // 2]:.0%} of each, and "
            f"{sum(1 for share in occupancy if share >= 0.9) / len(occupancy):.0%} of them "
            f"at least 90%"
        )
        # and how crowded they are
        channel.line(
            f"  tenants: a median of {sorted(tenants.values())[len(tenants) // 2]} chunks per "
            f"page, at most {max(tenants.values())}"
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
                # repeat the point
                for trial in range(self.trials):
                    # read the clocks
                    wall = time.perf_counter()
                    cpu = time.process_time()
                    # render the tile through the full pipeline, encoder included
                    dataset.render(
                        channel=pipeline,
                        zoom=(zoom, zoom),
                        origin=self._origin(dataset=dataset, span=span, zoom=zoom),
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
            # building the levels of the product, unless asked not to
            f"--qed.app.pyramids={'yes' if self.levels else 'no'}",
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
            # fetch the tile; a small team behind many clients over a remote product can keep
            # a request waiting in line for minutes, which is a result rather than a failure
            with urllib.request.urlopen(url, timeout=900) as response:
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

    # private data
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
