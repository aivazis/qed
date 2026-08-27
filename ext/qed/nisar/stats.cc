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
           const py::iterable & origin, const py::iterable & shape) -> stats_t {
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
           const py::iterable & origin, const py::iterable & shape) -> stats_t {
            // read and decode the tile, then collect its statistics
            return qed::nisar::statsBFPQ<grid_t>(
                source, datatype, asBFPQ(lut), asIndex<2>(origin), asShape<2>(shape));
        },
        // the signature
        "source"_a, "datatype"_a, "bfpq"_a, "origin"_a, "shape"_a,
        // the docstring
        "compute the statistics of a BFPQ encoded slc tile");

    // collect a mergeable sample of a strided complex slc tile
    m.def(
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
        "collect a mergeable statistical sample of the strided slc tile at {origin}+{shape}");

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
