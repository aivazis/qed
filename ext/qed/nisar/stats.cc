// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// stats
void
qed::py::nisar::stats(py::module & m)
{
    // bindings for HDF5 sources
    m.def(
        // the name of the function
        "stats",
        // the handler
        &qed::nisar::stats<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "datatype"_a, "origin"_a, "shape"_a,
        // the docstring
        "collect statistics on a subset of a dataset");

    m.def(
        // the name of the function
        "statsBFPQ",
        // the handler
        &qed::nisar::statsBFPQ<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "datatype"_a, "bfpq"_a, "origin"_a, "shape"_a,
        // the docstring
        "collect statistics on a subset of a BFPQ encoded dataset");

    // all done
    return;
}


// end of file
