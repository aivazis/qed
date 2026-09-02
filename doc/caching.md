<!-- -*- markdown -*-
     michael a.g. aïvázis <michael.aivazis@para-sim.com>
     (c) 1998-2026 all rights reserved
-->

# What qed remembers

This document describes what the server keeps between requests, what it recomputes, and why
the present arrangement is the wrong way round. It was written after a caching bug froze a
running server, and it records both the measurements that exposed it and the strategy that
follows from them. Companions: `doc/performance.md` sets out the measurement programme,
`doc/statistics.md` covers the display range, and `doc/diagnostics.md` lists the channels that
report on any of this.

## What is cached today

A tile request that misses the cache becomes a task for the crew of its data source. A worker
renders it, parks the encoded result in an unlinked temporary file, and passes the descriptor
back to the server; the team hands that file to the tile cache, which owns it from then on.
The cache is keyed on the complete render specification — reader, dataset, channel, zoom,
origin, shape, and the state of every controller in the visualization pipeline — and bounded
by a single budget, `capacity`, expressed in bytes of payload and defaulting to 128 MB. When
the budget is exceeded the least recently used entry is evicted and its file closed.

So the unit that is remembered is a **finished picture**: colormapped, encoded as a bitmap,
three bytes per pixel.

## What that costs

The following line came from the heartbeat of a server that had been running for an hour:

```
fds=197/256 waiting=0 | cache: 170 entries, 127.5MB of 128MB, 27 hits 858 misses
```

Three things are worth reading out of it.

**The byte budget works, and bounds the wrong quantity.** 127.5 MB over 170 entries is about
750 KB apiece, which is a 512×512 tile at three bytes a pixel. The cache is full and evicting
exactly as designed. But each of those 170 entries also holds an open file, and the process
may hold 256 descriptors in total. The cache alone is consuming two thirds of the ceiling
while reporting itself perfectly healthy.

**The descriptor cost is capacity divided by tile size, and nothing bounds it.** At 750 KB a
tile, 128 MB is 170 descriptors. At the 49 KB of a small tile it would be roughly 2700 — ten
times any ordinary ceiling. This is not hypothetical: it is what happened. The peek window
follows the cursor and asks for a small tile at an arbitrary origin many times a second, none
of which is ever requested again. A second or two of that filled the descriptor table, after
which everything that needed to open a file failed while the byte budget still read as
one-tenth full.

**The failure does not look like a failure.** A process out of descriptors cannot serve a
static asset, because that needs `open`, and cannot render a tile, because that needs a new
temporary file. It can still answer a GraphQL query, because that reads state already in
memory. So the server appears to be alive and answering while every browser attached to it is
dead. Diagnosing it from the outside took two days; the heartbeat now reports `fds` against
the limit precisely so it cannot take that long again.

**The hit rate is poor.** Twenty-seven hits against eight hundred and fifty-eight misses, for
128 MB of disk and 170 descriptors. Some of that is the shape of the session, but not all of
it, and the reason is structural: see below.

## The rule

> Remember what cost input and decompression. Deduce what costs arithmetic.

Reading a tile out of a compressed, chunked product is the expensive step. The library must
decompress every chunk the footprint touches whether or not the request keeps the cells.
Turning the resulting numbers into colours is a pass of arithmetic over data already in hand.

By that rule the present cache remembers the cheap half and recomputes the expensive one.

## Why a rendered tile is a poor thing to remember

A cached bitmap is reusable only by a request that agrees with it in every particular: the
same channel, the same zoom, the same origin, the same shape, and the same controller state.
That last term is the damaging one. The display range is part of the key, so moving a stretch
slider invalidates every cached tile of that dataset at once. The entries are not evicted —
they go on holding their bytes and their descriptors until the budget pushes them out — they
simply become unreachable. Much of the observed hit rate is explained by that alone.

The decompressed source region underneath the same tile is reusable by:

- every channel of the dataset, since `covariance` and `covarianceMasked` read identical cells;
- every controller setting, because the stretch is applied afterwards;
- the peek and the mosaic alike, since both read the same chunks;
- the statistics pass, which today re-reads a footprint the render has just read.

One remembered chunk therefore serves many deductions. One remembered picture serves one.

## What is already remembered well

The pyramid is the counter-example, and the model to follow. A dataset's decimated levels are
built once, stored beside the product in the workspace, and read at unit stride thereafter.
They are expensive to compute, they never change once written, and they are useful to every
request that looks at that dataset at that scale, whatever it intends to draw. That is what
remembering should look like: costly to produce, stable, and indifferent to how the answer
will eventually be presented.

The whole-dataset statistics keep the same company. They fall out of the pass that builds the
first level, and they are stored beside it, so a pyramid found on disk arrives with the
numbers it was the cheapest way to compute.

The pyramid is right about what to remember and wrong about where it puts it. Its levels live
in one HDF5 file per product, which only one process may write; a second writer is refused by
the library rather than made to wait. That, and not the granularity of the work, is what
holds first contact to a single worker. Each level is becoming a flat file of chunk-shaped
tiles in packing order, memory mapped for reading and written by many workers at disjoint
offsets. `pyramid.md` describes the format, the occupancy record that keeps sparse levels
honest about the fill value, and what pyre still lacks. Where that bears on this document it
is noted below.

## The unit of work

The viewer works with a tile shape identical to the chunk shape at every zoom level. That
establishes the invariant the rest of this section rests on:

> A viewed tile requires a predictable integer number of chunks to be decompressed.

**The zoom is a pair of integers, not one.** The two axes are decoupled: a view may be zoomed
out horizontally while held at full resolution vertically, and asking for a single zoom level
anywhere in this system is a bug. Everything below is per axis.

The count is one when a decimated level exists at the requested zoom on both axes, since the
level is then read at unit stride and the tile is exactly one of its chunks. Otherwise the
nearest usable level is the deepest that over-decimates neither axis, and each axis makes up
its own difference by striding. If those residual exponents are `rv` and `rh`, the footprint
covers a `2^rv` by `2^rh` block of that level's chunks, so the count is `2^(rv + rh)` — which
is a square only in the particular case where the user has left the axes coupled. Either way
the count is known, and it is known *before* the tile is served.

That is what makes the chunk a schedulable unit rather than merely a conceptual one. The cost
of a request can be computed from its specification, so work can be sized, divided and routed
on the basis of it, instead of on a count of output pixels that says nothing about what the
request will cost. It also means a tile at deep zoom decomposes into many chunks, which fan
out across the team of their own accord — the spread that affinity has to preserve rather than
manufacture.

What remains outside the invariant is a request that is not chunk-aligned at all, and the peek
window was exactly that. Its tiles are 128×128 at an origin
that follows the cursor, so each one straddles chunk boundaries, can never be served from a
level, and is never requested twice. Those renders now go to a route of their own and are
drawn on the server's thread without a worker, a spool, or a cache entry.

## Worker affinity

If the thing remembered is a decompressed chunk, then which worker holds it matters, and the
work should be routed to the worker most likely to have it already. A deterministic map from
`(dataset, level, chunkRow, chunkColumn)` to a member of the team gives that for nothing.

Two properties are wanted, and they pull against each other.

**Revisits must land on the same worker.** This is what makes the chunk cache worth having:
panning back over ground already covered should cost nothing.

**Neighbours must land on different workers.** A pan asks for a contiguous run of chunks, and
if a run maps to one member the rest of the team sits idle while it works. A map such as
`(row + column) mod N` spreads an axis-aligned run perfectly and sends a diagonal one entirely
to a single worker; a mixing hash scatters in every direction at the cost of some imbalance
over small sets. The choice is not obvious and should be made against a measurement of how
people actually pan.

**Affinity must be a preference and never a binding.** If the member that owns a chunk is busy
while others are idle, the work must go to an idle member anyway, and simply miss its cache.
Strict affinity reintroduces head-of-line blocking: one slow member accumulating a queue while
the rest of the team sits on the bench. That is the failure shape this system has already
demonstrated it is prone to, and an optimisation that reintroduces it is not worth its hit
rate.

## Decided, and open

Decided, and implemented:

- The peek window's tiles are rendered inline and never cached; they are one-offs by
  construction, and they were the workload that exhausted the descriptor table.
- The heartbeat reports `fds` against the process limit, alongside the cache's entry count,
  byte occupancy and hit rate, so this class of failure announces itself.

Decided, not yet implemented:

- The cache needs a second bound, on entries, because descriptors and not bytes are the
  resource that runs out. It is containment rather than a fix, and it should stay small.
- The server should raise its own descriptor limit at startup rather than inherit whatever
  the launching shell happened to have.

Answered by the pyramid on disk, described in `pyramid.md`:

- Whether the cache should hold decompressed chunks rather than rendered tiles. It should not
  hold them itself. A level stored as a flat file of chunk-shaped tiles is memory mapped, and
  the operating system's page cache is then the chunk cache: it costs one descriptor per level
  rather than one per remembered item, the descriptor may be closed as soon as the mapping
  exists, and no byte budget has to be invented for it. The argument above was right that
  chunks are the thing worth remembering, and wrong that the server should be the one
  remembering them.
- Whether the byte budget survives once entries are chunks. The question lapses with the
  answer above: the budget continues to govern rendered tiles, which are what the cache still
  holds, and mapped levels are governed by eviction of levels rather than by a byte count.

Open, and wanting a decision:

- Whether a payload should travel as a descriptor at all. Passing bytes over the crew channel
  removes descriptors from the transport as well as the cache, at the price of a copy that is
  negligible for a small tile and less so for a large one.
- Which mixing function routes chunks to workers, and how affinity degrades under load.


<!-- end of file -->
