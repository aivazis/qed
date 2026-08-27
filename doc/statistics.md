<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# dataset statistics: what we know, and the constraints on the code

> Status: **reference**. This document records what has been measured and built around dataset
> statistics — the numbers that drive the visualization controllers — and the invariants any
> further work must respect. It exists to prepare the retirement of the construction-time
> statistics sample, the one remaining piece of the original design.

## The two generations of statistics

qed has two statistics mechanisms side by side.

The **legacy sample** is a single 256×256 tile read from the center of each dataset when the
reader establishes first contact (`_collectStatistics` in the dataset constructors). Its
`(min, mean, max)` triple feeds `autotune`, which sets both the controller *picks* (`low`,
`high` — the values that shape pixels) and the *bounds* (`min`, `max` — the slider range).
It is a poor estimator: it sees one fixed window, so features outside it — bright
scatterers, the poles of a synthetic raster, anything off-center — are invisible, and the
initial color stretch is wrong everywhere the center is unrepresentative.

The **accumulator** arrived with the minimap thumbnail work. Every tile a crew renders is
also sampled: the worker revisits the exact decimated footprint the render saw and ships a
mergeable record — `(count, min, mean, m2, max)` over the magnitude of the source values,
NaN-skipping, Welford form — in the spool's pickled state. `Team.collect` drains records
into `Store.accumulate`, which folds them into a per-dataset `qed.ux.Sample` using the
parallel form of Welford's update, so partial results combine exactly regardless of arrival
order. When the accumulated range escapes a controller's bounds, the bounds *widen* — log
ranges to the next whole decade, linear ranges with a 5% hysteresis slack — and the store
broadcasts the coalesced change frame so live clients refetch and their sliders stretch in
place. The dataset thumbnail, a few-thousand-pixel mosaic of chunk-aligned slices, is the
pass that guarantees full-extent coverage; ordinary viewing keeps refining.

## What has been measured

- Statistics are cheap where data is already flowing. A full pass runs at amplitude
  throughput, ~300 Mcells/s; the per-tile sample adds a few operations per pixel, well under
  half a millisecond for a 512² tile of warm data.
- On compressed HDF5 the sample is **not** cheap when it forces its own read: the worker
  currently re-reads the decimated footprint after the render, which re-decompresses the
  chunks. The 7.6 GB GSLC thumbnail went from ~6 s to ~12 s when sampling landed. Fusing the
  sample into the render kernels — one pass, statistics collected as pixels flow — removes
  this, at the cost of touching every channel kernel and its bindings.
- Cached BMPs are useless for statistics: post-colormap, clipped to the stretch. Statistics
  must be collected where *source* values flow.
- The decimated grid is a good estimator. It is a uniform subsample of the whole raster: on
  the c16 test function it found the pole magnitude (~2654) that the center sample cannot
  see, and correctly widened the amplitude bounds from [-1, 1] to [-1, 4] in log space.
- NaN fill is excluded by the kernels, so a swath product accumulates swath-only statistics;
  the record `count` can be far below the footprint size, and an all-NaN tile contributes an
  empty record that merges as a no-op.
- The same footprint is re-sampled whenever it re-renders — a channel switch, a stretch
  change. Duplicate records are harmless to `min`/`max` but bias `count`/`mean`/variance
  toward frequently viewed regions. Fine for range control; not a calibrated statistic.

## The invariants

These are the rules the current code enforces, and that any change must preserve.

1. **Controller picks are part of tile identity.** `low`/`high` (and the value controllers'
   settings) shape pixels; the task identity harvest includes them, and the tile cache and
   in-flight dedup key on that identity. Any statistics-driven change to a pick MUST roll
   the affected view sessions and broadcast the change frame, so clients refetch; anything
   less silently serves stale tiles or floods the cache with orphans.
2. **Controller bounds are presentation.** `min`/`max` are declared `cosmetic` on the
   controllers and excluded from the identity harvest, so widening them never invalidates
   cached work and never rolls a session. `widen` only ever expands, never touches picks,
   and preserves the `dirty` flag — `dirty` is harvested, so flipping it would also perturb
   identity.
3. **Pinned controllers never move.** `auto: no` gates both `autotune` and `widen`; the test
   fixtures pin their pipelines for determinism and rely on this absolutely.
4. **The autotuners are shape-sensitive and unguarded.** `LinearRange._autotune` and
   `LogRange._autotune` unpack a bare `(low, mean, high)`; the channel wrappers index into
   the sample, and the isce2 unwrapped flavor expects a *list of two* triples for its
   line-interleaved bands. `autotune(stats=None)` must become a no-op before the legacy
   sample can retire.
5. **`GDALBand.render` reads `self.stats` on every tile** — the one render-time consumer.
   GDAL needs lazy statistics or another range source before retirement.
6. **Seeding cannot rely on ordinary tile traffic.** `LinearRange` defaults its picks to
   `None`; an untuned render of a linear channel crashes in the worker before it produces a
   statistics record — the record that would have seeded the controller. This chicken-and-egg
   is why initial statistics belong at **crew assembly**: when a team forms, stats-only
   stripe tasks (deep stride, chunk-aligned, one per worker) run ahead of renders and seed
   the accumulator without needing a working pipeline.
7. **The worker-side autotune is waste.** Workers rebuild readers and pay the legacy sample
   only to have `_configure` overwrite the tuned values with the client's controller state.
   Retirement deletes this cost; nothing consumes it today.
8. **Accumulation runs on the server event loop.** `Team.collect` calls `Store.accumulate`
   inline; the merge is a handful of float operations and must stay that cheap. The client
   notification is coalesced, so a burst of adjustments collapses into one refetch.
9. **The accumulator is keyed by dataset name.** The task carries `dataset = pyre_name`
   outside its identity; statistics are per dataset, shared across channels, over `|value|` —
   the same convention the legacy sample established, so the two feeds are interchangeable.

## The retirement plan

The agreed direction, in order:

- **Seed once, widen after.** The first records to arrive for a dataset whose controllers
  have never been tuned run the full `autotune` — picks included — on the reference channels
  and every view clone, roll the affected sessions, and notify; every later record widens
  bounds only. This is the one moment statistics may move picks, and it is loud by design.
- **Initial statistics at crew assembly.** Team formation enqueues stats-only stripe tasks
  ahead of the first render, so seeding does not depend on a renderable pipeline (invariant
  6) and arrives concurrently, with per-worker file handles.
- **Guards before deletion.** `autotune` tolerates a missing sample in every flavor,
  including the list-shaped unwrapped case (4); GDAL gets lazy statistics (5). Only then
  does `_collectStatistics` leave the dataset constructors.
- **Open UX question**: whether the first tiles render untuned and re-render when the seed
  lands, or the first paint waits briefly for the seed. To be decided before implementation.

Further out: fuse the sample pass into the render kernels (removes the double read on cold
HDF5), extend `sample()` to GDAL and stack datasets, and the optional log-histogram for
amplitude from the original design sketch.


<!-- end of file -->
