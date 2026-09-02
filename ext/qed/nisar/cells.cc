// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// externals
#include "external.h"
// namespace setup
#include "forward.h"


// the kernels of one cell type, bound once per kind of raster they can read
namespace qed::py::nisar {
    // bind the decimation over a source of type {rasterT} and a destination of type {draftT}
    template <class cellT, class rasterT, class draftT>
    inline void bindDecimate(py::module & cell)
    {
        // the grid the tile passes through; it holds exactly the cells the raster holds
        using grid_t = heapgrid_t<cellT>;
        // build a tile of a pyramid level from the level below it
        cell.def(
            // the name
            "decimate",
            // the handler
            [](const rasterT & source, draftT & destination, const datatype_t & datatype,
               const py::iterable & origin, const py::iterable & shape,
               const py::iterable & stride) -> sample_t {
                // read the strided tile and deposit it in the destination
                return qed::nisar::decimate<grid_t>(
                    source, destination, datatype, asIndex<2>(origin), asShape<2>(shape),
                    asIndex<2>(stride));
            },
            // the signature
            "source"_a, "destination"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a,
            // the docstring
            "fill the {destination} tile at {origin}+{shape} by decimating {source} by "
            "{stride}, and report a mergeable statistical record of what it held");
        // all done
        return;
    }

    // bind the sample over a source of type {rasterT}
    template <class cellT, class rasterT>
    inline void bindSample(py::module & cell)
    {
        // the grid the kernel reads into
        using grid_t = heapgrid_t<cellT>;
        // collect a mergeable sample of a strided tile
        cell.def(
            // the name
            "sample",
            // the handler
            [](const rasterT & source, const datatype_t & datatype, const py::iterable & origin,
               const py::iterable & shape, const py::iterable & stride) -> sample_t {
                // read the decimated tile and sample it
                return qed::nisar::sample<grid_t>(
                    source, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride));
            },
            // the signature
            "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a,
            // the docstring
            "collect a mergeable statistical sample of the strided tile at "
            "{origin}+{shape}");
        // all done
        return;
    }

    // bind the kernels over cells of type {cellT} in their own submodule
    template <class cellT>
    inline void bindCell(py::module & m, const char * name, const char * doc)
    {
        // the grid the kernels read into. it holds exactly the cells the file holds: a
        // buffer laid out for one type and filled from a dataset of another is read back
        // as pairs, or halves, of whatever the file actually stored
        using grid_t = heapgrid_t<cellT>;
        // gather the kernels of this cell type under their own name, so a caller picks the
        // one that matches its raster rather than getting whichever was bound first
        auto cell = m.def_submodule(
            // the name of the cell type, spelled the way {qed.datatypes} spells it
            name,
            // its docstring
            doc);
        // the decimation: the first level reads the product, every level after it reads the
        // level below, and the destination is the draft of a pyramid level
        bindDecimate<cellT, dataset_t, draft_t<cellT>>(cell);
        bindDecimate<cellT, level_t<cellT>, draft_t<cellT>>(cell);
        // the sample reads the product or a level, whichever serves the zoom
        bindSample<cellT, dataset_t>(cell);
        bindSample<cellT, level_t<cellT>>(cell);
        // compute the display range of a tile; this reads the product at open time, before
        // any level exists
        cell.def(
            // the name
            "stats",
            // the handler
            [](const dataset_t & source, const datatype_t & datatype, const py::iterable & origin,
               const py::iterable & shape) -> stats_t {
                // read the tile and collect its statistics
                return qed::nisar::stats<grid_t>(
                    source, datatype, asIndex<2>(origin), asShape<2>(shape));
            },
            // the signature
            "source"_a, "datatype"_a, "origin"_a, "shape"_a,
            // the docstring
            "compute the statistics of the tile at {origin}+{shape}");
        // all done
        return;
    }
}    // namespace qed::py::nisar


// cells
void
qed::py::nisar::cells(py::module & m)
{
    // create the {cells} submodule
    auto cells = m.def_submodule(
        // the name of the module
        "cells",
        // its docstring
        "the raster kernels, one set per cell type");
    // the integers, signed and unsigned; masks and classification rasters live here
    bindCell<std::int8_t>(cells, "int8", "rasters of signed single byte integers");
    bindCell<std::uint8_t>(cells, "uint8", "rasters of unsigned single byte integers");
    bindCell<std::int16_t>(cells, "int16", "rasters of signed two byte integers");
    bindCell<std::uint16_t>(cells, "uint16", "rasters of unsigned two byte integers");
    bindCell<std::int32_t>(cells, "int32", "rasters of signed four byte integers");
    bindCell<std::uint32_t>(cells, "uint32", "rasters of unsigned four byte integers");
    // the floating point numbers; the geocoded covariance, coherence and phase rasters
    bindCell<float>(cells, "float32", "rasters of single precision reals");
    bindCell<double>(cells, "float64", "rasters of double precision reals");
    // and the complex pairs; the single look complex products and the off diagonal
    // covariance terms
    bindCell<std::complex<float>>(cells, "complex64", "rasters of single precision complex");
    bindCell<std::complex<double>>(cells, "complex128", "rasters of double precision complex");
    // all done
    return;
}

// end of file
