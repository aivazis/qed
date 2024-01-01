// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// profile
void
qed::py::native::profile(py::module & m)
{
    // bindings for {mapgrid_t} sources
    m.def(
        // the name of the function
        "profile",
        // the handler
        &qed::native::profile<mapgrid_t<char>>,
        // the signature
        "source"_a, "points"_a,
        // the docstring
        "collect values from a dataset along a path");

    m.def(
        // the name of the function
        "profile",
        // the handler
        &qed::native::profile<mapgrid_t<int8_t>>,
        // the signature
        "source"_a, "points"_a,
        // the docstring
        "collect values from a dataset along a path");

    m.def(
        // the name of the function
        "profile",
        // the handler
        &qed::native::profile<mapgrid_t<int16_t>>,
        // the signature
        "source"_a, "points"_a,
        // the docstring
        "collect values from a dataset along a path");

    m.def(
        // the name of the function
        "profile",
        // the handler
        &qed::native::profile<mapgrid_t<int32_t>>,
        // the signature
        "source"_a, "points"_a,
        // the docstring
        "collect values from a dataset along a path");

    m.def(
        // the name of the function
        "profile",
        // the handler
        &qed::native::profile<mapgrid_t<int64_t>>,
        // the signature
        "source"_a, "points"_a,
        // the docstring
        "collect values from a dataset along a path");

    m.def(
        // the name of the function
        "profile",
        // the handler
        &qed::native::profile<mapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "points"_a,
        // the docstring
        "collect values from a dataset along a path");

    m.def(
        // the name of the function
        "profile",
        // the handler
        &qed::native::profile<mapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "points"_a,
        // the docstring
        "collect values from a dataset along a path");

    // all done
    return;
}


// end of file
