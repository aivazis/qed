# The pyramid on disk

The pyramid is the set of decimated levels that make a zoomed out view cheap. Level one is
built by reading every allocated cell of the product; each level above it is built from the
one below at a quarter the size. The pass that builds level one is the only expensive thing
in the whole of first contact, and the whole-raster statistics fall out of it rather than
costing a pass of their own.

This note describes how the levels are stored, why the storage is changing, and what has to
exist before the change can be made.


## Why the current storage cannot be built in parallel

The levels are written into an HDF5 file today, one file per product version, holding the
levels of every dataset that product contains. `Pyramid.path` resolves to
`{workspace}/pyramids/{stamp}.h5`, and `Pyramid._attach` opens it `r+`.

A single HDF5 file cannot be written by more than one process. Two processes attempting the
open that `_attach` performs produce, in the second one:

    H5FD__sec2_lock(): unable to lock file, errno = 35,
    error message = 'Resource temporarily unavailable'

The HDF5 in use is a serial build, so there is no parallel path to fall back on. Two further
details matter to anyone writing code against this. The refused open does not raise: it hands
back a `File` whose `hid` is `-1`, and only the error stack on stderr says anything, so the
`try`/`except` in `_attach` never fires and a broken handle propagates into `build`. And the
restriction applies to writers only — four processes opening the same product read-only all
succeed, because readers take a shared lock.

The consequence is that the granularity of the work is not what limits the concurrency.
Splitting level one into per-chunk tasks changes nothing while the destination is one HDF5
file: the workers would decimate in parallel and then queue behind a single lock, and the
serialized part would be the compressed write rather than the read it was supposed to hide.


## The layer file

Each level becomes one flat file holding its tiles in chunked packing order, padded so that
every tile occupies the same number of bytes.

The format needs no definition of its own, because it is the byte image of a grid pyre
already describes. `pyre::grid::chunked_t` stores each tile contiguously and orders the tiles
row-major; `tests/pyre.lib/grid/chunked_offset.cc` pins this, asserting for a 4×6 box diced
into 2×3 tiles that stepping along the fast axis within a tile advances one cell, that the
next row of the same tile follows immediately, that crossing a tile boundary skips a full
tile of storage, and that crossing along the slow axis skips a full row of tiles. A layer
file is therefore the storage of a `grid_t<chunked_t, map_t<cellT>>` and nothing more. The
offset of a cell is `packing.offset(index)`, and the offset of a tile is the offset of its
first cell. Neither has to be written.

Mapping the file once yields both access patterns a client might want. A reader that takes
whole tiles gets contiguous bytes and useful readahead; a reader that wants an arbitrary cell
gets pointer arithmetic. qed is the first kind and the viewer is built around it, but the
second costs nothing extra.

Edge tiles are padded to the full tile shape. This is not a new decision: `chunked_t` already
sizes itself that way, and the h5 tiling test asserts a cell count of `(4*30) * (3*40)` for a
100×100 extent diced into 30×40 chunks, the overhang included.

The layout on disk mirrors the HDF5 hierarchy it replaces. The group path of a dataset within
its product becomes a directory path, and each level is a file within it:

    {workspace}/pyramids/{stamp}/{dataset path}/level-{nn}.tiles
    {workspace}/pyramids/{stamp}/{dataset path}/level-{nn}.occupancy
    {workspace}/pyramids/{stamp}/{dataset path}/pyramid.json

The stamp continues to identify the product version, so a cache built against one version is
never read against another. The level number is zero padded so the levels list in order. The
sidecar records the layout the levels were built for, their format version, the cell type,
the shape and the tile, and the statistics measured while level one was built; a sidecar
written for another layout is ignored.

The levels stop at the one that fits within a single tile. A deeper zoom is served by
striding that one tile, which is already the cheap case, so nothing above it would buy
anything; a raster that fits in a tile to begin with gets no levels at all.


## Writing without contention

One process sizes the file to its full padded extent before any tile is written. The file is
sparse: the regions nobody writes occupy no blocks.

Every worker then writes whole tiles at computed offsets. The ranges are disjoint by
construction, since a tile belongs to exactly one unit of work, so concurrent writes need no
lock and no coordination. This is the property the HDF5 file could not offer.

Because the levels are built one from another, level *n* still depends on level *n−1*. It
does not depend on all of it: a tile of level *n* is built from a 2×2 block of tiles of level
*n−1*, so a level may begin as soon as the tiles it needs exist rather than waiting for the
level below to complete. The pyramid becomes a pipeline instead of a sequence of barriers.
This is a property of the storage, not of the scheduler, and it is unavailable while one
process owns one file.


## Sparsity, and why it needs a record

A tile that holds nothing but fill should cost nothing. In the HDF5 storage this was free:
an unwritten chunk has no entry in the chunk table, and the library returns the fill value on
request. A sparse flat file loses that, because the hole reads back as zero bytes.

Zero is not the fill value. The pyramid fills with `cell.blank`, which is NaN for real and
complex cells, and the viewer colours declared fill and undeclared NaN differently on
purpose. A tile read out of a hole would arrive as `0.0`, which is a legitimate measurement
rather than an absence, and would be drawn as data.

So the level carries an occupancy record naming the tiles that were actually written.
Anything not named is entirely fill, and a reader synthesizes fill for it without touching
the mapping. Three properties are wanted of it:

- **One byte per tile, not one bit.** Workers write their own entries concurrently, and a bit
  field would make two workers read, modify and write the same byte. At one byte per tile a
  level of six hundred tiles costs six hundred bytes, which is not worth a race.
- **It is the commit record.** An entry is written after the tile it names is durable, so a
  worker that dies mid-tile leaves a tile nobody will read. This replaces the write-to-
  temporary-and-rename that a file-per-tile layout would have needed.
- **The server may own it instead.** Workers already report completion, and the server is
  already the place where their statistics are merged. Having the server write the record
  keeps the workers write-only with respect to shared state.


## What pyre does not yet have

pyre has an out-of-core mosaic, but it is not sparse. `pyre::memory::Paged` gives each page
three state bits — `resident`, `valid` and `clean` — and its own documentation records that
`release` "returns a page to the never-touched state, indistinguishable from one that was
never brought in." A page that nobody has asked for yet and a page that is known to hold
nothing but fill are therefore the same state, and there is no way to say that a read should
be answered from fill rather than from the backing store.

Two ways forward, and they are not exclusive.

The **near-term** one keeps the sparsity in qed. A level is read as
`grid_t<chunked_t, constmap_t<cellT>>` — a plain mapping with no paging, since the operating
system already pages it — and the reader consults the occupancy record before reaching into
the mapping. Nothing changes in pyre, and the mosaic machinery is not involved at all.

The **general** one puts the notion in pyre, so that a mosaic can carry the fill value and
answer a read for an absent tile without a backing store access. That is a fourth piece of
per-page state rather than a fourth bit on `Paged`, since "absent because it is empty" is a
property of the grid's relationship to its source and not of the allocation. It is the right
home for the idea, and it would serve `pyre::h5`'s mosaics too, where an unwritten chunk is
exactly the same situation.

The near-term path is the one to take first, because it can be measured before any pyre
change is committed to.


## What is given up

The levels are compressed today, with `shuffle` and `deflate` at level four. A mapped flat
file is not compressed, and adding compression back would defeat the mapping.

Two things offset this. Reads get faster rather than slower, because a tile becomes a mapped
page with no inflation at all, and tile reads are the hot path while pyramid writes happen
once. And a sparse file spends no disk on fill, which recovers much of what compression gave
for exactly the products where it matters — a geocoded product framed loosely enough to be
mostly fill now occupies nothing for the empty part, rather than occupying the small but
non-zero cost of compressing it.


## Consequences elsewhere

Mapping a layer answers a question left open in `caching.md`. The server does not need to
cache decompressed chunks, because a mapped level is already a cache managed by the operating
system, and it costs one descriptor per level rather than one per cached item. The descriptor
may be closed as soon as the mapping exists, since the mapping outlives it.

Eviction becomes possible at a useful granularity. The current cache is one file per product
and can only be deleted whole; it never shrinks. A directory of levels can be evicted a level
at a time, which is what makes a disk budget tractable.


## Open questions

- Whether the occupancy record is written by the workers or by the server. The server is
  simpler and matches where the statistics already flow; the workers avoid a round trip.
- Whether tiles are ordered row-major or by a locality-preserving curve. Row-major matches
  `chunked_t` and needs no new code; a Morton order would serve diagonal panning better, and
  the question should be settled by measuring how the viewport actually moves.
- Whether all levels of a dataset share one file with computed level offsets, rather than one
  file per level. One file means one mapping and one descriptor; separate files make a level
  independently evictable and independently rebuildable.
- What the reader does when the occupancy record and the tile file disagree, which is what a
  crash between the two writes looks like.


<!-- end of file -->
