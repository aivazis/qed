// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// profile
void
qed::py::isce2::interferogram::profile(py::module & m)
{
    // bindings for {mapgrid_t} sources
    m.def(
        // the name of the function
        "profile",
        // the handler
        &qed::native::profile<mapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "points"_a, "closed"_a,
        // the docstring
        "collect values from a dataset along a path");

    m.def(
        // the name of the function
        "profile",
        // the handler
        &qed::native::profile<mapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "points"_a, "closed"_a = false,
        // the docstring
        "collect values from a dataset along a path");

    // all done
    return;
}


// end of file
