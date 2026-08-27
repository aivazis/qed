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

## The instrument

The `qed measure` panel drives the program: `measure tile` sweeps tile generation over shape,
zoom, and channel, recording one flat record per request — wall and cpu clocks, both denominators,
a cache-state label; `measure fit` fits the accumulated records to `a + b·pixels` on both axes and
reports the wall−cpu character per group; `measure swarm` launches the installed server, fires
concurrent clients at a workload of distinct tiles with the tile cache disabled, and records the
throughput at each concurrency level, while the `qed.ux.tiles` diagnostic captures the server-side
view of every request. Invocation from a directory whose `qed.yaml` names the datasets:

```
qed --shell=script measure tile
qed --shell=script measure fit
qed --shell=script measure swarm --team=4 --clients=1,2,4,8
```

## Measurement categories

Each section records its own setup, raw numbers, the `a`/`b` fit, the wall/cpu character, and the
serial-fraction reading that feeds Amdahl.

### 1. Data fetch

> Status: **first numbers, flat/memmap only** (2026-08-27, 16-core arm64, 128 GB). The
> measurements below cover ONLY the native reader, whose memory-mapped source makes the fetch
> nearly free once pages are resident; nothing here transfers to HDF5, and even less to HDF5 over
> S3, where the fetch is expected to dominate. Those modalities are the next sweeps.

**Flat/memmap, warm** (c16 fixture, 3929×6049 complex64, all pages resident): on the vary-zoom
axis the slope is indistinguishable from zero — at fixed 512² output, growing the source footprint
4× and 16× moves the request time by fractions of a millisecond, with poor r² because there is no
line to fit. `wall ≈ cpu` throughout (gap 0%), confirming the fetch is compute, not waiting.
Warm memmap fetch is, as predicted, free; the cold/faulted-in case is not yet measured (requires
eviction discipline the harness does not yet have).

**HDF5, local disk, warm** (7.6 GB NISAR GSLC, complex64, 4 GB page buffer, file resident in the
page cache after the first pass): at zoom 0 the slopes match memmap exactly — amplitude ~3.4,
phase ~16.4 ns/px — the fetch disappears into the pipeline. Zooming out changes that: at zoom 1
amplitude jumps to ~24 ns/px and phase to ~36; at zoom 2, ~30 and ~43. The fetch is no longer
free even fully warm: the strided hyperslab must run the libhdf5 machinery over 4× and 16× the
source cells, and it multiplies the zoomed-out render cost by up to ~9× over memmap. Read per
*source cell* the marginal cost falls with zoom (~5.2 ns/cell at zoom 1, ~1.6 at zoom 2),
pointing at chunk-granularity costs amortizing — the decimate-during-fetch question of category 2
is live for this modality. Still `wall ≈ cpu` throughout: warm HDF5 is bound on decompression and
library work, not waiting. The cold first-touch and the S3/`ros3` cases — where the wall−cpu gap
should finally open — remain unmeasured.

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

> Status: **first numbers, flat/memmap source** (2026-08-27; source cost is ~zero warm, so these
> slopes are nearly pure pipeline+encode).

On the vary-output-shape axis (256–2048, fixed zoom, warm), per output pixel:

| channel   | `b`          | throughput   | `a`       | r²      | wall−cpu |
|-----------|--------------|--------------|-----------|---------|----------|
| amplitude | 3.1–4.1 ns   | ~250–330 Mpx/s | ≈ 0.1 ms | ≥ 0.98 (zoom 0,1) | 0% |
| phase     | 15.6–16.4 ns | ~61–64 Mpx/s | ≈ −0.8–−0.1 ms | ≥ 0.999 | 0% |

The fits are clean lines; the fixed cost `a` is negligible at real tile sizes, so this stage is
purely marginal-cost. Phase pays ~5× over amplitude — the `atan2` — which also prices the complex
channel (amplitude + phase + the double source traversal). Everything is `cpu ≈ wall`: the
pipeline parallelizes across cores until cores run out. A byproduct worth recording: at these
rates, REAL statistics are cheap — a full pass over the fixture's 24 Mcells at the amplitude
throughput is ~80 ms, and accumulating min/max/histogram during a render adds a few ops per pixel
(well under 0.5 ms on a 512² tile). The open-time center-sample shortcut saves essentially nothing
on this modality.

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

## First parallel validation

> Status: **measured, flat/memmap workload only** (2026-08-27, 16 cores/12P+4E, 128 GB).

`measure swarm`, 64 distinct 256² tiles of the complex channel, cache disabled, 8 concurrent
clients, sweeping the team size:

| team | throughput |
|------|------------|
| 1    | 107 tiles/s |
| 2    | 120 |
| 4    | 135.5 |
| 8    | 142.8 |
| 12   | 138.8 |

One crew already delivers 75% of peak; 1→8 crews buys only 1.33×; 12 regresses. Amdahl fitted to
the curve gives a serial fraction near **0.7**: the ceiling (~143 tiles/s ≈ 7 ms/tile) is the
single-threaded server event loop — request parse, task build, spool adoption, mmap, response
write — not render capacity. The server-side diagnostic confirms it: under load, ~50 ms wall
against ~4 ms cpu per request is queueing, not work. Two consequences: on this machine and this
workload the optimal team size is **4** (within 5% of the ceiling), and the next win is thinning
the serialized path, not recruiting more crews. Expensive tiles (larger shapes, HDF5 sources,
stack reductions) grow the parallel fraction and shift the optimum up — to be measured, not
assumed.

Cache sizing, from the same numbers: a rendered tile costs ~3 bytes per output pixel (×4/3 for a
zoom pyramid), so full coverage of the c16 fixture is ~96 MB per channel and a NISAR GSLC-scale
product runs ~1.2 GB per channel. The 128 MB default is conservative; on a 128 GB machine a
multi-GB budget is comfortable, and the spools live in the page cache, so the pressure is soft.

## Toward the conclusion

When the four categories are measured, each contributes an `a`, a `b`, and a wall/cpu character.
From those we assemble the serial fraction `s` of end-to-end tile generation — the part bound on
shared resources that contention will serialize — and Amdahl's law gives the ceiling on what any
amount of parallelism can return, along with the point of diminishing returns. The conclusion is
expected to be easy to anticipate. The purpose of this program is to make it **inescapable**
instead.

<!-- end of file -->
