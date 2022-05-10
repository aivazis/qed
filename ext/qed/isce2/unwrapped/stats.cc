// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// stats
void
qed::py::isce2::unwrapped::stats(py::module & m)
{
    // bindings for {mapgrid_t} sources
    m.def(
        // the name of the function
        "stats",
        // the handler
        &qed::isce2::unwrapped::stats<mapgrid_t<float, 3>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a,
        // the docstring
        "collect statistics on a subset of a dataset");

    // bindings for {mapgrid_t} sources
    m.def(
        // the name of the function
        "stats",
        // the handler
        &qed::isce2::unwrapped::stats<mapgrid_t<double, 3>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a,
        // the docstring
        "collect statistics on a subset of a dataset");

    // all done
    return;
}


// end of file
