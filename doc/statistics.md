<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# dataset statistics: what we know, and the constraints on the code

> Status: **reference**. This document records what has been measured and built around dataset
> statistics — the numbers that drive the visualization controllers — and the invariants any
> further work must respect. The construction-time sample has since been retired as a
> construction-time cost; what remains of it, and what replaced it, is recorded below.
> Companion: `doc/staging.md` for the lifecycle that now owns the seeding moment.

## The two generations of statistics

qed has two statistics mechanisms side by side.

The **seed sample** is a single 256×256 tile read from the center of each dataset. It used
to be taken inside every dataset constructor, so it was paid by anyone who built a dataset
for any reason. It is now taken only when somebody asks, through `measure()`, and the
callers that ask are the ones that need the numbers: a reader opening on the blocking path,
and a crew member conducting a survey, whose record carries the result to the server as the
seed a hydrated twin tunes itself from. Its `(min, mean, max)` triple feeds `autotune`,
which sets both the controller *picks* (`low`, `high` — the values that shape pixels) and
the *bounds* (`min`, `max` — the slider range). It remains a poor estimator: it sees one
fixed window, so features outside it — bright scatterers, the poles of a synthetic raster,
anything off-center — are invisible, and the initial stretch is wrong wherever the center
is unrepresentative. Replacing *what* it measures is the work that remains; *when* it is
measured is settled.

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

## The seed: what it probes, and what that costs

The seed is no longer a single window in the middle of the raster. It is a grid of windows
spread across the full extent, each one the dataset's own tile — the chunk shape, for a
product that has one — with its origin snapped to a multiple of that shape. Alignment is
not a detail: a window that straddles a boundary obliges the library to decompress as many
as four chunks to deliver the cells of one.

Measured on a 7.6 GB NISAR GSLC whose data occupies a stripe in one corner, sixteen windows
per dataset:

| strategy | time | non-fill cells found |
|---|---|---|
| one 256² window in the center (what this replaced) | — | 0 |
| 256² windows, unaligned | 23.1 ms | 65,536 |
| 512² windows, unaligned | 28.5 ms | 262,144 |
| 512² windows on chunk boundaries | 13.7 ms | 262,144 |

Chunk alignment is worth 2.1× against windows of the same size, and the aligned probe is
still 1.7× faster than the smaller unaligned one while sampling four times the data. The
whole four-dataset product is probed in about 15 ms per dataset. The center window, for
comparison, found nothing at all on **every one of the four datasets** and fell back to
nominal values — the display range of that product was previously a fabrication.

## The whole-dataset pass, and whether crews help

The pass that touches every chunk is the minimap thumbnail: it decimates the raster until
its long axis is about two thousand pixels and chops the result into chunk-aligned slices,
each an ordinary tile request. It is the only workload that sees all the data, and its
statistics already flow into the accumulator. `qed measure crew` sweeps it across team
sizes. On the same product, twenty-five slices at stride 32, local disk:

| team | wall | speedup |
|---|---|---|
| 1 | 33.2 s | 1.00× |
| 2 | 17.4 s | 1.91× |
| 4 | 10.7 s | 3.10× |
| 8 | 9.1 s | 3.65× |
| 16 | 9.0 s | 3.69× |

Sixteen workers are no faster than eight, and the knee is at four. The reason is not
bandwidth but load imbalance: eight of the twenty-five slices carry 94% of the work, and
the slowest single one takes 7.8 s, so no crew can finish the pass faster than that plus
overhead — which is the 9 s plateau, arrived at from below. The cheap slices cover fill,
which HDF5 returns without reading anything. Raising the ceiling therefore means cutting
the slices finer, not hiring more workers.

Two caveats worth carrying. First, this is a local, uncompressed-cache measurement: a
repeat of the single-worker pass at the end of the sweep took 34.9 s against 33.2 s cold,
so with 128 GB of memory and a 7.6 GB file the cost is plainly decompression rather than
I/O. Second, and consequently, **none of this transfers to S3**, where the pass starts out
I/O bound and additional workers buy overlap of fetch latency rather than of CPU; the
shape of that curve has not been measured.

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
4. **The autotuners are shape-sensitive, and now guarded.** `LinearRange._autotune` and
   `LogRange._autotune` unpack a bare `(low, mean, high)`; the channel wrappers index into
   the sample, and the isce2 unwrapped flavor expects a *list of two* triples for its
   line-interleaved bands. `autotune(stats=None)` is a no-op — in `Controller.autotune` for
   every leaf controller, and in the three isce2 unwrapped channels that index before
   delegating — so a dataset nobody has measured keeps its configured values instead of
   raising. Any new shape-sensitive autotuner must carry the same guard.
5. **`GDALBand.render` takes its range from the controller.** It used to read `self.stats`
   on every tile, which silently ignored the client's settings; it now reads `low` and
   `high` off the channel's `range` controller, which is what the worker installs the
   client's state onto.
6. **Seeding does not rely on tile traffic.** `LinearRange` defaults its picks to `None`,
   and an untuned render of a linear channel would crash in the worker before it could
   produce the record that would have seeded the controller. The survey dissolves this: a
   crew member measures the product during first contact, and the twin the server hydrates
   is tuned before any view can bind it, so no render is ever attempted against an untuned
   pipeline. This is why the seeding moment belongs to staging rather than to crew assembly,
   which is where an earlier draft of this document placed it.
7. **Workers do not measure.** A worker rebuilding a reader for a render passes
   `measure=False`, so no dataset samples itself; `_configure` then installs the client's
   controller state, which is what the render must honor anyway. A survey passes
   `measure=True`, because the numbers are its deliverable.
8. **Accumulation runs on the server event loop.** `Team.collect` calls `Store.accumulate`
   inline; the merge is a handful of float operations and must stay that cheap. The client
   notification is coalesced, so a burst of adjustments collapses into one refetch.
9. **The accumulator is keyed by dataset name.** The task carries `dataset = pyre_name`
   outside its identity; statistics are per dataset, shared across channels, over `|value|` —
   the same convention the legacy sample established, so the two feeds are interchangeable.

## What the retirement actually did

The plan this document once carried has been overtaken by the staging redesign, which
supplied a better answer to the question the plan was trying to solve. What was done:

- **Seeding moved to the survey.** A crew member measures each dataset during first contact
  and the record carries the numbers; hydration tunes the twin's channels from them. This is
  the one moment statistics may set picks, and it is guaranteed to precede any view binding
  the dataset, so no session is ever rolled on account of a seed and no user watches a
  re-tune. The stats-only stripe tasks the plan proposed are no longer needed for seeding.
- **Measurement left construction.** `_collectStatistics` survives, but as the body of
  `measure()`, called by whoever wants numbers rather than by everyone who builds a dataset.
- **The worker's throwaway sample is gone.** A render no longer pays for statistics it
  discards; measured directly, an unmeasured open of the GSLC fixture is meaningfully
  cheaper and produces identical pixels, since the client's controller state governs.
- **Guards landed.** Invariant 4 holds in every flavor, including the list-shaped unwrapped
  case; GDAL renders from its controller rather than from `self.stats`, and gained a
  `survey()` and a hydrated construction path, so it is no longer the flavor that cannot be
  surveyed.
- **The open UX question dissolved.** First tiles cannot render untuned, because the panel
  does not populate until the survey lands.

- **The center window is gone.** The seed now probes a chunk-aligned grid across the whole
  extent, as recorded above, and an all-fill product is told it is all fill instead of
  being handed an invented range in silence.

What remains, in rough order of value:

- **Statistics from the whole-dataset pass may set picks, not just widen bounds.** The
  probe is a good estimator, but the thumbnail pass is a better one and it already runs.
  Its records currently widen bounds only, because moving a pick after a view is bound
  would roll sessions (invariant 1). Letting the pass run during staging, before anything
  is bound, would remove that objection — at the cost of the seconds measured above, which
  is why the cheap probe seeds and the expensive pass refines.
- **Cut the whole-dataset pass into finer slices.** Its parallel ceiling is set by its
  slowest slice, not by the crew size; smaller slices would raise it.
- **Fuse the sample pass into the render kernels.** Still worthwhile: the per-tile sample
  re-reads the decimated footprint, which doubles the cost on cold HDF5.
- **`sample()` for GDAL and stack datasets**, so their tiles contribute to the accumulator
  the way memmap and NISAR tiles do.
- The optional log-histogram for amplitude from the original design sketch.


<!-- end of file -->
