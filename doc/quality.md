<!--
-*- markdown -*-
-*- coding: utf-8 -*-

michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# quality: how a product sits in its file

> Status: **built in part** (qed#110). The measurements, the `layout` query, the census reference,
> and the panel with its scorecard, census comparison, chunk map, page strip, their linking, and the
> histograms are in place; the read cost overlay, the `window.qed.quality` namespace, and a
> Playwright behavior spec are not. The sections below keep the design as it was proposed, with
> notes where the build differs.

What a tile costs depends as much on how a product was written as on the reader: how its
chunks sit on the pages of the file, which datasets share those pages, whether the chunks that
share a page are neighbors on the raster, and whether the writer wrote chunks that hold nothing
but the fill. `qed measure pages` and the census built on it (`doc/performance.md`) measure all of
this from the metadata of the file and a chunk or two per raster, and report it as numbers. This
document proposes a panel that draws the same measurements for the product being viewed, so the
layout of a product can be seen at a glance, and compared against the census of its kind.

The panel serves two audiences: a user wondering why one product is slower than another, and the
writers of the products, for whom the pictures make the recommendations of the census concrete.

## What the server does

### The measurements

Everything the panel draws is computed by `qed.readers.pages`, which `qed measure pages` uses as
well, for local products and products in S3 alike:

- **the chunk table of every dataset in the file**: the address, stored size, and origin of each
  written chunk, and the shape of the chunk grid, which also says which chunks were never written;
- **the page size and file space strategy** of the file, and its size;
- **the storage of the datasets the reader does not display**, which share the pages;
- **the fill**: the value the library knows about, the `_FillValue` attribute, what the smallest
  chunk holds, and which chunks hold the same bytes;
- **the summary record** of each raster: the three amplifications, the fill of its pages, the
  nearly empty and unwritten shares, the locality.

Only the fill check reads data, one to three pages per raster.

### The query

A top level GraphQL query, `layout(dataset: String!)`, beside the pixel `sample`. The store
computes the description the first time it is asked for, through `realize`, which opens the
product in the server process the way the pixel peek does, and keeps it, since the layout of a
product does not change while it is connected; disconnecting the source lets go of it. The walk
of the storage of the file is kept per product, so the other rasters of the same product cost only
their fill check. A product that is not an HDF5 file has no layout, and the query answers `null`.

`Layout` carries:

- the storage settings: the file space strategy, the page size, zero for a file without pages, the
  size of the file, the shape of the raster and of its chunks, its cell, and its filters;
- `summary`: the occupancy record: the chunks written and nearly empty, the bytes they store, the
  three amplifications, the fill of the pages, the locality, and the histograms;
- `partners`: the datasets that share the pages of the raster, and their bytes on them;
- `fill`: the fill the library knows about, the `_FillValue` attribute, what the smallest chunk
  holds, whether the two agree, the chunks that hold nothing but the fill, and the time to decode,
  make, and encode one;
- `grid`: for every cell of the chunk grid, in row major order, its state (`unwritten`, `fill`,
  `sliver`, `data`), the stored size of its chunk, and the page the chunk starts on; a sliver is a
  nearly empty chunk that is not all fill;
- `strip`: for every page the raster lands on, in file order, the bytes of the raster, the number
  of its chunks, the bytes of every other dataset, and the other dataset with the most bytes on it;
  `null` for a file without pages;
- `census`: the comparison against the rasters of the same kind in the latest census of the
  product, `null` without one.

A large GSLC has about 22,500 chunks per raster and 3,000 pages per raster; as parallel arrays of
integers that is a few hundred kilobytes, delivered once.

### The census, as reference

The census digests are fluid, so the server does not ship them: the `census` trait of the plexus
names a folder, e.g. `qed.app.census: ~/data/census` in `qed.yaml`, and the server reads every
`digest-*.json` in it, written by `qed measure digest`, the first time a layout is asked for. It
keeps the latest cycle of each product, and compares a raster against the rasters of the same kind
in it, e.g. a covariance term `HHHH` against the other `HHHH` rasters rather than against the masks.
An unset trait, a missing folder, or a file that cannot be read means only that there is no
comparison, with at most a warning on the `qed.census` channel.

## What the client does

### The activity

A new activity, `quality`, on the navigation rail right above `journal`, following the pattern of the
console: a directory under `ux/client/activities/quality`, a shape, one line in the bar. It sits
in the `viz` layout beside `controls` and the readers, so the panel can be read next to the
viewport of the raster it describes. It follows the dataset selected in the active viewport.

### The views

In order of importance.

**The chunk map.** The chunk grid of the raster, one cell per chunk, drawn on a canvas at the
aspect of the raster, colored by state. It is the view that shows the fill at a glance: a GCOV is
a swath of data inside a solid frame of written fill; a GSLC is the same swath with most of the
frame never written and a fringe of fill along the edges.

```
  chunk map: L.A.HHHH                          . never written   # data
                                               x fill            ~ sliver
  +--------------------------------------+
  |x x x x x x x x x x x x x x x x x x x |     written      1089 of 1089
  |x x x x x x x ~ # # ~ x x x x x x x x |     fill          572  (53%)
  |x x x x x ~ # # # # # # ~ x x x x x x |     slivers        70
  |x x x ~ # # # # # # # # # # ~ x x x x |     data          447
  |x x ~ # # # # # # # # # # # # # ~ x x |
  |x x x ~ # # # # # # # # # # # # # ~ x |     declared fill  0.0  (default)
  |x x x x x ~ # # # # # # # # # # # ~ x |     _FillValue     nan
  |x x x x x x x ~ # # # # # # # # ~ x x |     fill holds     nan        [x] differ
  |x x x x x x x x x ~ # # # # # ~ x x x |
  |x x x x x x x x x x x x x x x x x x x |
  +--------------------------------------+
```

A toggle, *not built yet*, shades the data chunks by compression ratio instead, which shows where
the scene is busy and where it is uniform.

**The file map.** *Built as two trays. The `pages` tray is the page strip of the raster: the pages
it lands on, each filled with the bytes of the raster, of the other datasets, and the room left
over. The `file map` tray is the whole file, told apart by lightness rather than by a color per
raster: the raster in view, the other rasters of the product, the datasets the product does not
display, and the metadata or free space. The rasters are listed under the map; hovering one lights
up its pages and a click pins it. Chunks of fill count as their raster's bytes; the chunk map is the
view that tells them apart. A file that is not paged has no file map. Hovering a page in either
tray names what it holds.* The pages of the file, one cell per page, laid
out in rows of a fixed width in file order. Each cell is a small stacked bar of the datasets on it,
in the colors of a legend; pages that hold chunks of fill are hatched, and pages that hold no raw
data are grey. It is the view that shows interleaving: a GSLC whose HH and HV polarizations were
written at the same time shows pages split between the two colors, where an RSLC shows long runs of
one.

```
  file map: 1270 pages of 4 MiB                 H L.A.HH   V L.A.HV   m mask
                                                o other    - metadata or free
  page    0: - - - - H H H H H H H H H H H H H H H H H H H H H H H H H H H H
  page   32: H H H H H H H H H H H H H H H H H H H H H H H H H H H H H H H H
  page   64: H H H H H H H H H V V V V V V V V V V V V V V V V V V V V V V V
  page  704: V V V V V V V V V V V V V V V V V V V V V V V H/V H/V V/H H/V V
  ...
                        hover: page 727, 4 MiB
                          L.A.HH   2.1 MiB   2 chunks
                          L.A.HV   1.9 MiB   2 chunks
```

**The two maps, linked.** Hovering a chunk on the chunk map highlights its page on the file map,
and outlines on the chunk map every other chunk on that page, of any raster of the product. The
chunks a reader of one tile pays for, and whether they are its neighbors, then show up directly:
a compact outline around the hovered chunk is good locality; outlines scattered across the raster
are poor locality. Hovering a page on the file map outlines its chunks on the chunk map.

```
  chunk map, hovering chunk (7, 12)             file map
  +--------------------------+                  page 351: H H [H] H
  |# # # # # # # # # # # # # |                    outlined on the chunk map:
  |# # # # # # # # # # # # # |                    (7,11) (7,12) (7,13) (8,12)
  |# # # # # # # # # # #[#][#]|                   all neighbors: locality 1.0
  |# # # # # # # # # # # #[#]|
  +--------------------------+
```

**The read cost overlay.** *Not built yet.* The chunk map colored by what fetching each chunk costs
a reader that fetches whole pages: the bytes of its page over its own bytes, alone or together with
its page mates. A second mode applies it to the viewport: for the tiles on screen, the bytes fetched
against the bytes needed, which connects the layout to the wait the user sees.

**The scorecard.** *Built as two trays for the raster in view: `layout`, with its numbers and the
fill check, and `census`, with a sparkline per measure, drawn by the `widgets/histogram` widget,
marked where the raster falls.* One row per raster of the product, with a gauge per measure: the read
amplification alone and together, the fill of its pages, the locality, the shares of the grid
unwritten and of the written chunks that are fill, and a badge that says whether the fill the
library knows about is what the fill chunks hold. Behind each gauge, a sparkline of the census
distribution for the kind of product, with a mark where this raster falls.

```
  scorecard                     this raster       census of GSLC, cycle 31
                                                  p10          median        p90
  read alone, x                    1.62           |-----------[====|=]-------|
  read together, x                 1.05           |--[=|=]-------------------|
  page fill                        0.73           |------[=====|=]-----------|
  locality                         0.58           |------[=|===]-------------|
  written chunks that are fill     0.25           |----------[==|==]---------|
  grid never written               0.35           |---------[==|====]--------|
  declared fill agrees             yes
```

**The histograms.** The stored size of the chunks as a share of their raw size, and the share of
each page the raster fills, as in the progress report, drawn live for this product.

### Markup and automation

The panel carries `data-qed-panel="quality"`; the scorecard and the census are regions with a
`data-qed-measure` on each row; the maps carry `data-qed-view` with their names (`chunk-map`,
`page-strip`), the chunk under the pointer is reflected in `data-qed-chunk` and the page in focus
in `data-qed-page`; the bars of the histograms carry `data-qed-bin` and `data-qed-count`. Not built
yet: a `quality` namespace on `window.qed`, with `quality.layout(dataset)` returning the query and
`quality.hover(chunk)` driving the linked highlight.

## Tests

- `tests/qed.pkg/pages.py`: the chunk codec, the states of a chunk grid, and the strip of pages,
  on chunk tables worked out by hand.
- `tests/qed.pkg/layout.py`: the description of the rasters of the GCOV fixture, which is written
  the way the GCOV writer does it: the fill the library knows about differs from the one the
  rasters hold.
- `tests/qed.pkg/measurements_census.py`: the reference data of a census, and the measures of a
  raster by the names the census gives them.
- the identity and ARIA sweeps of the Playwright suite visit `/quality`. Not built yet:
  `tests/qed.ux.playwright/behavior/quality.spec.ts`: the panel mounts, the counts match the query,
  hovering a chunk highlights its page and its page mates.

## Change map

`qed`:

- `pkg/readers/pages.py`: the description of a raster: storage, paging, occupancy, fill, the
  states of the chunk grid, and the strip of pages, shared with `qed measure pages`.
- `pkg/measurements/census.py`: the reference data of a census, and the measures of a raster.
- `pkg/cli/Measure.py`: `measure digest` writes the reference data as json.
- `pkg/shells/Plexus.py`: the `census` trait, the folder of the census digests.
- `pkg/ux/Store.py`: `layout` and `census`, and the release of both on disconnect.
- `pkg/gql/layout/` *(new)*: `Layout` and its parts; `pkg/gql/Query.py`: the `layout` query.
- `ux/client/widgets/histogram/` *(new)*: the histogram widget.
- `ux/client/activities/quality/`, `ux/client/shapes/quality/` *(new)*: the activity.
- `ux/client/views/viz/quality/` *(new)*: the panel and its trays.
- `ux/client/widgets/flex/`: a flex box lets the mouse events through unless a panel is flexing.

## Sequencing

Built, in order: the server side; the scorecard, the chunk map, and the histograms; the census
comparison; the page strip and its linking to the chunk map. Next: the read cost overlay, the
`window.qed.quality` namespace, and the behavior spec.

## Open questions

1. **Every raster, or the selected one?** Settled for now: the panel describes the raster in the
   active view, and the page strip shows the pages that raster lands on; a map of every page of the
   file, with the selected raster emphasized, remains possible.
2. **When is the layout computed?** Settled: on demand, when the panel first asks, and kept.
3. **Products that are not HDF5.** The panel says there is no layout to show; a chunk map for
   formats with tiles remains possible.
4. **Where the census reference comes from.** Settled: a folder the user configures, since the
   digests change with every census.


<!-- end of file -->
