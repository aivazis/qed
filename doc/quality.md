<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# quality: how a product sits in its file

> Status: **design**, for discussion. Nothing described here is built yet.

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

Everything the panel draws is already computed by `qed.readers.pages` and `Measure._nodata`, for
local products and products in S3 alike:

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

A GraphQL field on a dataset, `layout`, resolved lazily when the panel asks for it, and cached on
the dataset once computed, since a product's layout does not change while it is open:

- `summary`: the record of `occupancy`, plus the fill;
- `chunks`: parallel arrays of the chunk grid coordinates, stored sizes, pages, and a state per
  chunk (`unwritten`, `fill`, `sliver`, `data`, where a sliver is a nearly empty chunk that holds
  some data);
- `pages`: for each page of the file, the bytes of each dataset on it, as a list of
  `(dataset, bytes)` pairs, and whether it holds any chunk of fill; the pages that hold no raw data
  are metadata or free space;
- `datasets`: the names of the datasets on the pages, including the ones the reader does not know,
  under their paths in the file.

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

A new activity, `quality`, on the navigation rail after `journal`, following the pattern of the
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

A toggle shades the data chunks by compression ratio instead, which shows where the scene is
busy and where it is uniform.

**The file map.** The pages of the file, one cell per page, laid out in rows of a fixed width in
file order. Each cell is a small stacked bar of the datasets on it, in the colors of a legend;
pages that hold chunks of fill are hatched, and pages that hold no raw data are grey. It is the
view that shows interleaving: a GSLC whose HH and HV polarizations were written at the same time
shows pages split between the two colors, where an RSLC shows long runs of one.

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

**The read cost overlay.** The chunk map colored by what fetching each chunk costs a reader that
fetches whole pages: the bytes of its page over its own bytes, alone or together with its page
mates. A second mode applies it to the viewport: for the tiles on screen, the bytes fetched
against the bytes needed, which connects the layout to the wait the user sees.

**The scorecard.** One row per raster of the product, with a gauge per measure: the read
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

The panel carries `data-qed-panel="quality"`; the maps carry `data-qed-view` with their names,
and the hovered chunk and page are reflected in `data-qed-chunk` and `data-qed-page`, so the
Playwright suite can drive the linking without coordinates. `window.qed` gains a `quality`
namespace: `quality.layout(dataset)` returns the query, and `quality.hover(chunk)` drives the
linked highlight.

## Tests

- `tests/qed.pkg/`: the chunk states and the page occupancy for small synthetic products, one
  with a declared fill and unwritten chunks, one with written fill and an undeclared fill, and one
  whose rasters are interleaved; the same fixtures the census tests use.
- `tests/qed.ux.playwright/behavior/quality.spec.ts`: the panel mounts, the counts match the query,
  hovering a chunk highlights its page and its page mates.

## Change map

`qed`:

- `pkg/readers/pages.py`: the chunk states and the per page breakdown, factored out of
  `occupancy` and `Measure._nodata` so the census and the panel compute the same things.
- `pkg/gql/Layout.py` and its parts *(new)*: the `layout` field on a dataset.
- `pkg/shells/Plexus.py`: the `census` trait, the folder of the census digests.
- `ux/client/activities/quality/`, `ux/client/shapes/quality/` *(new)*: the activity.
- `ux/client/views/viz/quality/` *(new)*: the panel, the maps, the scorecard, the histograms.
- `ux/client/automation/qed.js`: the `quality` namespace.
- `doc/automation-surface.md`: a pointer.

## Sequencing

1. The server side: chunk states, page breakdown, the `layout` field. Verifiable from GraphQL
   before any client work.
2. The chunk map with its counts and the fill badge.
3. The file map, and the linking of the two.
4. The scorecard, with the census reference data.
5. The read cost overlay, and the histograms.

## Open questions

1. **Every raster, or the selected one?** The chunk map is per raster; the file map is per file.
   Showing the file map for the whole product, with the selected raster emphasized, is proposed.
2. **When is the layout computed?** On demand, when the panel first asks, is proposed; computing it
   at first contact would add a page fetch or two per raster to opening every product, in S3 too.
3. **Products that are not HDF5.** Flat files and GDAL rasters have no pages to draw; the panel
   says so, and could still show the chunk map where the format has tiles.
4. **Where the census reference comes from.** Settled: a folder the user configures, since the
   digests change with every census.

<!-- end of file -->
