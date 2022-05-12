// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// profile
void
qed::py::isce2::unwrapped::profile(py::module & m)
{
    // bindings for {mapgrid_t} sources
    m.def(
        // the name of the function
        "profile",
        // the handler
        &qed::isce2::unwrapped::profile<mapgrid_t<float, 3>>,
        // the signature
        "source"_a, "points"_a,
        // the docstring
        "collect values from a dataset along a path");

    m.def(
        // the name of the function
        "profile",
        // the handler
        &qed::isce2::unwrapped::profile<mapgrid_t<double, 3>>,
        // the signature
        "source"_a, "points"_a,
        // the docstring
        "collect values from a dataset along a path");

    // all done
    return;
}


// end of file
