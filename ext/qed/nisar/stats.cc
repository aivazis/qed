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
    // the BFPQ kernels are the one place where the cells in memory are not the cells in the
    // file: the product stores a quantized integer pair per sample, and the lookup table
    // turns it into a complex number on the way in. so their grid is fixed, and the kernels
    // that read a raster as it stands are bound per cell type in {cells}
    using grid_t = heapgrid_t<std::complex<float>>;

    // compute the statistics of a BFPQ encoded slc tile
    m.def(
        // the name
        "statsBFPQ",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype, const py::buffer & lut,
           const py::iterable & origin, const py::iterable & shape) -> stats_t {
            // read and decode the tile, then collect its statistics
            return qed::nisar::statsBFPQ<grid_t>(
                source, datatype, asBFPQ(lut), asIndex<2>(origin), asShape<2>(shape));
        },
        // the signature
        "source"_a, "datatype"_a, "bfpq"_a, "origin"_a, "shape"_a,
        // the docstring
        "compute the statistics of a BFPQ encoded slc tile");

    // collect a mergeable sample of a strided BFPQ encoded slc tile
    m.def(
        // the name
        "sampleBFPQ",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype, const py::buffer & lut,
           const py::iterable & origin, const py::iterable & shape,
           const py::iterable & stride) -> sample_t {
            // read and decode the decimated tile, then sample it
            return qed::nisar::sampleBFPQ<grid_t>(
                source, datatype, asBFPQ(lut), asIndex<2>(origin), asShape<2>(shape),
                asIndex<2>(stride));
        },
        // the signature
        "source"_a, "datatype"_a, "bfpq"_a, "origin"_a, "shape"_a, "stride"_a,
        // the docstring
        "collect a mergeable statistical sample of the strided BFPQ tile at {origin}+{shape}");

    // all done
    return;
}


// end of file
