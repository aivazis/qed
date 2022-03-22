// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"
// stats datasets
#include "stats.h"


// stats
void
qed::py::datasets::stats(py::module & m)
{
    // bindings for {mapgrid_t} sources
    m.def(
        // the name of the function
        "stats",
        // the handler
        &statsGrid<mapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a,
        // the docstring
        "collect statistics on a subset of a dataset");

    // bindings for HDF5 sources
    m.def(
        // the name of the function
        "stats",
        // the handler
        &statsHDF5<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a,
        // the docstring
        "collect statistics on a subset of a dataset");

    // all done
    return;
}


// end of file
