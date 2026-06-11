<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# qed performance: framing the problem

> Status: **framing**. This document sets up the performance measurement program for tile
> generation. The introduction below fixes the question, the cost model, and the measurement
> discipline. Each measurement category then gets its own section, filled in as hard numbers
> land, so the document accumulates toward a single, measured conclusion rather than an assumed
> one.

## The question

The expensive thing in qed is **tile generation**: the work the server does between receiving a
tile request and handing back an encoded image. Everything that feels slow — pans, zooms, redraws,
multi-client sync — is many tile generations stacked up.

The target framework is **Amdahl's law**. Speedup from throwing resources at a problem is capped by
the fraction of the work that stays serial:

```
speedup(N) = 1 / ( s + (1 - s)/N )      ->   1/s  as N -> infinity
```

where `s` is the serial fraction — work that does not parallelize, either because it is inherently
sequential or because it is bound on a *shared* resource (a single storage device, the memory bus, a
global lock) that contention serializes anyway.

We are deliberately **not** assuming what `s` is. The conclusion about parallelism — how much it
buys, and where diminishing returns set in — must *fall out of measurement*, not be anticipated. The
job of this document is to measure the serial single-thread cost structure of tile generation in
enough detail that `s` is read off the numbers, per stage, with confidence.

## What "tile generation" is

A tile request resolves to a `viewport` and, through its server-side state, to a dataset, a channel,
a zoom level (a pair), an origin, and an output shape. Generation is a pull-driven chain: the
encoder walks the output raster pixel by pixel and pulls values back through the visualization
pipeline, which pulls decimated source data from the reader. Four stages, in cost order of interest:

1. **Data fetch** — get enough source data to satisfy the requested tile footprint. Four source
   modalities, each with its own cost character (below).
2. **Decimation** — reduce the fetched footprint to the effective shape at the requested zoom. Can
   happen *after* the fetch (stride in memory) or *during* it (reader-native decimation).
3. **Visualization pipeline** — per-pixel transforms dictated by the channel: projections, scaling,
   shifting, colormap lookup, and — for dataset stacks — reductions over multiple sources.
4. **Rendering / encoding** — serialize the colored raster into an image stream. Currently
   Microsoft BMP without alpha.

These four are the **measurement categories**. Each gets a section below.

## The cost model

For any stage, in a single thread, we fit the per-request time to a two-parameter line:

```
time(request) = a + b · pixels
```

- **`a`** — fixed per-request cost, independent of size: reader open/seek, the open-time statistics
  touch, pipeline-iterator instantiation, first chunk-cache warm, encoder header.
- **`b`** — marginal per-pixel cost; its inverse `1/b` is the steady-state throughput in pixels/sec.

The split matters more than either number alone. If `a` dominates at real tile sizes, the work is
overhead-bound. If `b` dominates, the next question is *what `b` is bound on* — and that is read
directly off the **wall − cpu gap** (the `qed.timers` wall/cpu pair already wired into the
dispatcher):

| Observation        | Marginal cost is bound on | Implication for `s` |
|--------------------|---------------------------|---------------------|
| `cpu ≈ wall`       | CPU                        | parallel across cores until cores exhausted |
| `wall ≫ cpu`       | I/O or memory stall       | parallel only overlaps the waits; ceiling is the *device's* concurrency, not core count |

This is the bridge to Amdahl: the per-stage `a`, `b`, and wall/cpu character together forecast both
the *magnitude* of any parallel win and *where it saturates* — without running a parallel test. The
parallel conclusion is then derived, not assumed.

### Two denominators

At a fixed output tile, the only way "request size" varies is via zoom — the source footprint grows
while the output pixel count stays constant. So "per pixel" is ambiguous and we sweep **two
independent size axes**, each isolating a different slope:

- **Vary output shape** (256 / 512 / 1024 / 2048) at fixed zoom → per-**output**-pixel throughput.
  Loads the pipeline and encoder; the slope here is render-bound. This is where the BMP-vs-paletted
  question lives.
- **Vary zoom** at fixed output shape → per-**source**-element throughput. Loads fetch and
  decimation; the slope here is I/O-bound. This is where the four modalities and the
  decimate-before/after question separate.

Same `a + b·pixels` fit on each, with the matching denominator, and the wall/cpu gap on both.

## Measurement discipline

Three rules keep the numbers honest.

1. **Label cache state.** At least four caches stack under a tile: the OS page cache (which *is* the
   substance of memory-mapped "random access" — deferred page faults, not free reads), the libhdf5
   chunk cache, the 4 GB HDF5 page buffer, and for S3 whatever `ros3` holds. The open-time statistics
   sample also pre-touches the dataset center, so the "first tile" near center is **not** cold. Every
   number is labeled **cold vs warm**, and cold runs actively evict (fresh process / fresh region /
   dropped caches) or the comparison is meaningless. For memmap specifically, distinguish
   *faulted-in* from *resident*.

2. **Isolate out of process.** Measure each stage with a direct harness that calls the reader, the
   decimator, the pipeline, and the encoder at their boundaries — *not* through the HTTP server and
   browser, whose scheduling and lazy-load timing add variance unrelated to the stage under test.

3. **Storage layout is a first-class variable.** Source modality is not the whole story: chunked vs
   contiguous, compressed vs not, and chunk dimensions change the answer — especially for the
   decimation question, because on a chunked+compressed dataset the chunk is the atomic
   read+decompress unit.

The instrument is the existing `qed.timers` wall/cpu pair; the wall − cpu gap is the single most
useful number, and it is already collected per request in `pkg/ux/Dispatcher.py`.

---

## Measurement categories

Each section records its own setup, raw numbers, the `a`/`b` fit, the wall/cpu character, and the
serial-fraction reading that feeds Amdahl.

### 1. Data fetch

> Status: **not yet measured.**

Four modalities, swept against storage layout, on the *vary-zoom* axis (per-source-element):

- **Flat binary, memory-mapped** — page-fault bound; expect `wall ≫ cpu` on cold pages, `cpu ≈ wall`
  once resident.
- **HDF5, local disk** — libhdf5 read cost per tile; split by contiguous vs chunked+compressed.
- **HDF5, S3 via `ros3`** — a category of its own; measure **byte-range request count**, not just
  wall time, since request granularity and weak caching dominate.
- **GDAL-hosted** — least understood; add "has overview pyramids?" as a variable, since native
  overviews make decimated reads nearly free.

### 2. Decimation: before vs after

> Status: **not yet measured.**

Compare decimate-after (stride the fetched buffer) against decimate-during (reader-native: HDF5
strided hyperslab, GDAL `buf_xsize`/`buf_ysize`). The hypothesis is that the winner is
**layout-dependent**, not modality-uniform: a clear win for contiguous/uncompressed, possibly a wash
for chunked+compressed where whole chunks are read and inflated regardless of stride, and possibly a
large win for GDAL-over-overviews. Measure bytes touched and chunks/byte-ranges touched, not only
time.

### 3. Visualization pipelines

> Status: **not yet measured.**

Measure each implemented channel pipeline separately on the *vary-output-shape* axis
(per-output-pixel). Expected to be small until stack reductions, with two asterisks: the complex
channel currently traverses source twice, so part of its "pipeline" cost is hidden I/O; and stack
reductions scale with **member count**, which is where pipeline cost stops being flat — so member
count is a first-class axis here.

### 4. Rendering / encoding

> Status: **not yet measured.**

Isolate encode cost on the *vary-output-shape* axis. BMP-no-alpha is near-zero CPU (memcpy + header)
but fat on the wire. The trade to measure against it:

- Compressed lossless (PNG, WebP-lossless): real CPU for smaller payloads — relevant for remote /
  WAN / AWS-hosted clients, not for LAN.
- **Paletted output**: a colormap with ≤256 entries makes the natural tile an *indexed* image; PNG-
  palette is both small and cheap because it matches the data's real entropy. Most promising
  lossless direction.
- Lossy (WebP/AVIF) is **off the table** for a quantitative visualizer — banding/ringing reads as
  data.
- The one non-bandwidth reason to move is **alpha**, for nodata/masked regions (NISAR masks).

---

## Toward the conclusion

When the four categories are measured, each contributes an `a`, a `b`, and a wall/cpu character.
From those we assemble the serial fraction `s` of end-to-end tile generation — the part bound on
shared resources that contention will serialize — and Amdahl's law gives the ceiling on what any
amount of parallelism can return, along with the point of diminishing returns. The conclusion is
expected to be easy to anticipate. The purpose of this program is to make it **inescapable**
instead.

<!-- end of file -->
