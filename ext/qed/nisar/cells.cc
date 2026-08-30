// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// the helpers that bind the kernels of one cell type
namespace qed::py::nisar {
    // bind the kernels that read a raster whose cells are {cellT}
    template <typename cellT>
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

        // build a tile of a pyramid level from the level below it
        cell.def(
            // the name
            "decimate",
            // the handler
            [](const dataset_t & source, const dataset_t & destination, const datatype_t & datatype,
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

        // collect a mergeable sample of a strided tile
        cell.def(
            // the name
            "sample",
            // the handler
            [](const dataset_t & source, const datatype_t & datatype, const py::iterable & origin,
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

        // compute the display range of a tile
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
