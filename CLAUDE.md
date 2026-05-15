# qed — project context for Claude Code

## What qed is

qed is a web-based visualizer for very large scientific rasters (SAR, NISAR,
ISCE2 interferograms, and generic flat/HDF5/GDAL files). The browser client
requests 512×512 tiles as `<img>` elements via lazysizes lazy-loading; tiles
are rendered on-demand by a Python/C++ server.

## Stack layers (top to bottom)

| Layer | Path | Role |
|-------|------|------|
| React client | `ux/client/` | Tile requests as `<img>` elements |
| HTTP server | `pkg/shells/Plexus.py` | pyre HTTP server (synchronous, single-threaded) |
| URL routing | `pkg/ux/Dispatcher.py` | Tile request handler |
| Orchestration | `pkg/ux/Store.py`, `Viewport.py`, `View.py` | Python-side tile logic |
| Bindings | `ext/qed/` | pybind11 bridge |
| C++ pipelines | `lib/qed/native/channels/` | Lazy-iterator viz: decimate → normalize → colorize → BMP encode |
| NISAR pipelines | `lib/qed/nisar/` | NISAR-specific readers and pipelines |
| Python readers | `pkg/readers/` | nisar, isce2, native, GDAL dataset readers |

## Data formats supported

- NISAR HDF5: RSLC, GUNW, GCOV, covariance, coherence, mask
- ISCE2 interferograms
- Memory-mapped flat binary
- GDAL-backed rasters

## Performance work (roadmap as of 2026-05-15)

### What is already efficient

- **Lazy C++ iterator pipelines** — `decimate_t → parametric_t → colormap → bmp_t.encode()` are fully lazy; no intermediate arrays.
- **BMP delivery** — `memoryview(tile)` in `pkg/ux/Dispatcher.py:172` is zero-copy to HTTP response.
- **HDF5 page buffer** — `pkg/readers/nisar/H5.py:33–96` sets a 4 GB aggregation cache (50% raw data).
- **Memory-mapped flat files** — `pkg/readers/native/datasets/MemoryMap.py` avoids read() syscalls.
- **Statistics at open time** — min/max sampled once from a 256×256 center tile; not repeated per request.

### Critical bottlenecks

1. **GIL held during all tile rendering** (`ext/qed/native/channels.cc` + nisar equivalents)
   — No `py::call_guard<py::gil_scoped_release>()` on any rendering function. Two concurrent tile requests serialize completely.
   — Fix: add `call_guard<py::gil_scoped_release>()` to every `channels.def()` call in the binding files.

2. **No tile cache** (`pkg/ux/Store.py`)
   — Every pan, zoom, or redraw re-renders from scratch.
   — Fix: LRU cache (50–200 MB) keyed on `(dataset, channel, zoom, origin, shape)`. Expect ~80% hit rate → ~10× latency reduction for cache hits.

3. **Synchronous single-threaded HTTP server** (`pkg/shells/Plexus.py`)
   — A single slow tile (HDF5 miss, GDAL over-read) freezes all concurrent requests.
   — Fix: thread pool wrapper or async HTTP adapter (larger change; depends on pyre architecture).

4. **GDAL reads full resolution before decimating** (`pkg/readers/native/datasets/GDALBand.py:104–112`)
   — `ReadAsArray()` fetches full-res; then `tile[::scale, ::scale]` discards most of it. At zoom −2 this wastes 4× the I/O.
   — Fix: use GDAL's native decimation (`buf_xsize`/`buf_ysize` params on `ReadAsArray`).

### Moderate bottlenecks

5. **Complex channel reads data twice** (`lib/qed/native/channels/complex.icc`)
   — Amplitude and phase pipelines traverse the same source data separately.
   — Fix: fuse into a single pass.

6. **Profile sampling is per-pixel HDF5 reads** (`lib/qed/nisar/profile.icc`)
   — Bresenham-style iteration with individual HDF5 accesses per sample.
   — Fix: batch reads into bounding-box slices; cache profile results.

7. **Statistics only from center sample** (`pkg/readers/nisar/products/Product.py:201–227`, `pkg/readers/native/datasets/GDALBand.py:171–178`)
   — Normalizer min/max from one fixed 256×256 center sample; color stretch is wrong outside that region.
   — Fix: on-demand stats for the visible region, or expose range controls (partial solution exists in `pkg/controllers/LinearRange.py`).

### Priority order

| Priority | Fix | Location |
|----------|-----|----------|
| Critical | Release GIL in all render bindings | `ext/qed/native/channels.cc` + nisar equivalents |
| Critical | LRU tile cache | `pkg/ux/Store.py` |
| High | GDAL native decimation | `pkg/readers/native/datasets/GDALBand.py:104–112` |
| Medium | Thread pool / async HTTP | `pkg/shells/Plexus.py` |
| Medium | Fuse complex pipeline passes | `lib/qed/native/channels/complex.icc` |
| Medium | Batch profile HDF5 reads | `lib/qed/nisar/profile.icc` |
| Low | On-demand stats for visible region | `Product.py`, `GDALBand.py` |

### Client-side issues

Client-side performance issues exist but have not been detailed yet.
