// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// the BFPQ lookup table helper
#include "bfpq_lut.h"
// namespace setup
#include "forward.h"


// stats
void
qed::py::nisar::stats(py::module & m)
{
    // the nisar kernels read a tile out of an h5 dataset (using {datatype} for the on-disk layout)
    // into a grid of a fixed cell type, then collect its statistics
    using grid_t = heapgrid_t<std::complex<float>>;

    // compute the statistics of a complex slc tile
    m.def(
        // the name
        "stats",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape) -> stats_t {
            // read the tile and collect its statistics
            return qed::nisar::stats<grid_t>(source, datatype, asIndex<2>(origin), asShape<2>(shape));
        },
        // the signature
        "source"_a, "datatype"_a, "origin"_a, "shape"_a,
        // the docstring
        "compute the statistics of a complex slc tile");

    // compute the statistics of a BFPQ encoded slc tile
    m.def(
        // the name
        "statsBFPQ",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype, const py::buffer & lut,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape) -> stats_t {
            // read and decode the tile, then collect its statistics
            return qed::nisar::statsBFPQ<grid_t>(
                source, datatype, asBFPQ(lut), asIndex<2>(origin), asShape<2>(shape));
        },
        // the signature
        "source"_a, "datatype"_a, "bfpq"_a, "origin"_a, "shape"_a,
        // the docstring
        "compute the statistics of a BFPQ encoded slc tile");

    // all done
    return;
}


// end of file
