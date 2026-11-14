<!--
-*- markdown -*-
-*- coding: utf-8 -*-

michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# iq rasters: samples stored as pairs of integers

> **Status, 2026-11-14.** The design questions are settled; nothing beyond the BFPQ rasters of
> NISAR's RRSD products is implemented. The guard that keeps reads of samples honest
> ([reading samples](#reading-samples)) is on the pyre branch `h5-compound-guard`.

Many radar products store each sample as a pair of integers: raw echoes as the instrument
digitized them, and single look complex images stored with integer parts. pyre has a cell for
them, `pyre::memory::iq_t<T>`, a pair of counts `i` and `q` with no arithmetic. This document
says how qed shows a raster of such samples, and which readers offer them.

## Decisions

All settled on 2026-11-14.

1. **What a sample is to the viewer.** The two counts, as stored, without interpretation: a good
   start for showing raw data. Showing the complex value a sample stands for is a later step
   ([decoders](#decoders)).
2. **Where the counts are pulled out.** A flow node splits a tile of samples into an `i` tile and
   a `q` tile, and the real valued pipelines draw each one; the iterator kernels get a matching
   projection as the fallback. On 2026-10-07, on a `c8` raster, whole-tile flow pipelines beat
   the iterators at 512² (median ms per tile: value 0.58 → 0.25, complex 5.4 → 3.55), while an
   extra stage costs on small tiles (amplitude at 128²: 0.053 → 0.077).
3. **Who knows the decoder.** The dataset: its reader knows the product, and a flat file takes it
   as a setting. Deferred until decoded channels are needed; today only BFPQ decodes.
4. **Pyramid levels.** None for these rasters, as for BFPQ.
5. **Names in `qed.datatypes`.** pyre's cell names, `iqint8` … `iquint64`, with GDAL's `cint16`
   and `cint32` as aliases for the signed ones.
6. **Which readers first.** Flat files and GDAL; NISAR's RRSD rasters, whose samples are
   `iquint16`, get the count channels beside their decoded BFPQ ones; CEOS raw products wait for
   a sample file.

## Design

A raster of samples is shown as it is stored. The flow node of decision 2 turns a tile of samples
into two integer tiles, and everything after it exists already: the value and colormap pipelines
take integer rasters as they are. The cursor reports both counts. With no pyramid levels, a
zoomed out view reads every second, fourth, … sample of the product itself; that is acceptable
from a local disk and slow from S3.

### Decoders

A decoder turns a pair into the complex value it stands for, and each product says which one
applies:

- widening, `(i, q) → i + jq`, for counts that are the parts of the value;
- a bias, `(i, q) → (i − b) + j(q − b)`, for raw echoes stored as unsigned counts around a
  midpoint, such as CEOS raw products, whose leader gives the bias of each component;
- a lookup table, `(i, q) → lut[i] + j·lut[q]`, for BFPQ.

qed has the third already: the BFPQ kernels (`lib/qed/nisar/bfpq/`) read a tile of
`iq_t<std::uint16_t>`, decode it through the table into a tile of `complex<float>`, and render
that with the native complex channels.

### Reading samples

hdf5 converts between compound types by matching the names of their members. NISAR names the two
counts of a sample `r` and `i`; the memory type pyre writes names them `i` and `q`. Reading a
NISAR raster through the latter succeeds and returns the wrong numbers: the file's second count
lands in `i`, and `q` is never written.

So every read of samples takes the member names from the dataset, by position:
`DataSet::pair(count)` builds a compound whose members carry the dataset's own names, at the
offsets of the fields `i` and `q`, and `DataSet::memtype<cellT>()` uses it for any `iq_t` cell.
In python, `memtype.aligned(dataset)` gives the same type, and `htype` for every other cell.

The reads that line up this way:

- pyre's `Raster.tile`;
- C++ reads that deduce their type: `pyre::h5::read<gridT>(dataset, origin, shape, stride)` and
  the mosaic fills;
- qed's `Product.memtype`, which every read of a NISAR product and its pyramid uses.

The low-level reads, python `DataSet.read(memtype=…)` and C++
`pyre::h5::read(dataset, datatype, …)`, accept any type. The pyre guard refuses, on a firewall,
any transfer through a compound memory type that names a member the dataset does not have; a
read that names a subset of the members is allowed.

Checked against the RRSD granule in `~/dv/data/nisar-rrsd`: `h5dump` of
`/science/LSAR/RRSD/swaths/frequencyA/txH/rxH/HH` shows `{"r": 172, "i": 169}` at
(1000, 1000), and qed reads `(i, q) = (172, 169)` there.

## Findings

Each checked in the code or the data on 2026-11-14.

- **pyre's cell.** `iq_t<T>`, byte order by composition (`iq_t<foreign_t<T>>`); hdf5 memtypes
  `IQInt8` … `IQUInt64`; memory mapped grids of cells named `iquint16`, `iqint16be` and so on;
  python sees a sample as the tuple `(i, q)` and a grid as the buffer format `T{H:i:H:q:}`.
- **The native kernels** take any buffer and pick their cell type from its format
  (`qed::py::onGrid` in `ext/qed/grid.h`); they know integers, floats and complex numbers, and do
  not recognize a record such as `T{H:i:H:q:}`.
- **`qed.datatypes`** has no type for a pair of integers; GDAL's `cint16` and `cint32` are marked
  as not yet implemented. A complex type offers the channels `complex`, `amplitude`, `phase`,
  `real` and `imaginary`.
- **GDAL** bands take their cell name from GDAL, `cint16` for a CInt16 band as in Sentinel-1 SLC
  GeoTIFFs, and read cells their format table does not list as doubles, which keeps the real part
  only. What a CInt16 band does end to end has not been run: no such file is on disk.
- **CEOS** refuses complex integer codes (`CI*…`), and `tests/qed.pkg/ceos.py` checks the
  refusal. Raw products declare such a code, so they are refused rather than misread: JAXA's ALOS
  PALSAR level 1.0 says `CI*1`, while ESA's ALOS RAW, JERS-1 level 0 and GDAL's CEOS driver say
  `CI*2` for the same layout, a pixel of two one-byte samples (descriptor fields 32–34: 8 bits per
  sample, 2 samples and 2 bytes per pixel), 3 or 5 of the bits significant. The number after `CI`
  is not used consistently, so the layout has to come from fields 32–34. Sources: JAXA's PALSAR
  level 1.0 format description, revision J; ESA's PLSR-CEOS specification, version 3.2; NASDA's
  JERS-1 user's guide; isce3's ALOS reader.
- **ENVI** headers have no data type for a pair of integers: pyre's header
  (`packages/pyre/envi/Header.py`) accepts the codes 1–6, 9 and 12–15, which name integers, reals
  and complex floats only.
- **Pyramids** store their levels in the cell type of the raster they decimate.

## Open questions

- What a CInt16 GDAL band does today, end to end.
- CEOS raw products need the bias decoder and a sample file: ERS-2 raw from MathWorks
  (`ERSData.zip`) and an ALOS level 1.0 set from GMTSAR (`ALOS_Baja_EQ.tar.gz`), both public.
- Whether python passes hdf5 types to the NISAR kernels at all, now that every kernel is compiled
  for one cell type and could deduce its own.


<!-- end of file -->
