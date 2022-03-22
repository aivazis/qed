// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"
// profile datasets
#include "profile.h"


// profile
void
qed::py::datasets::profile(py::module & m)
{
    // bindings for {mapgrid_t} sources
    m.def(
        // the name of the function
        "profile",
        // the handler
        &profileGrid<mapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "points"_a,
        // the docstring
        "collect values from a dataset along a path");

    // bindings for HDF5 sources
    m.def(
        // the name of the function
        "profile",
        // the handler
        &profileHDF5<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "datatype"_a, "points"_a,
        // the docstring
        "collect values from a dataset along a path");

    // all done
    return;
}


// end of file
