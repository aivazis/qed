// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for the nisar tile generators
void
qed::py::nisar::real(py::module & m)
{
    // create the {real} submodule
    auto real = m.def_submodule(
        // the name of the module
        "real",
        // its docstring
        "support for nisar {real} datasets");

    // {r4} amplitude
    real.def(
        // the name of the function
        "value",
        // the handler
        &qed::nisar::real::value<heapgrid_t<float>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the value of a float tile");
    // {r8} amplitude
    real.def(
        // the name of the function
        "value",
        // the handler
        &qed::nisar::real::value<heapgrid_t<double>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a double tile");


    // {r4}
    real.def(
        // the name of the function
        "abs",
        // the handler
        &qed::nisar::real::abs<heapgrid_t<float>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of a float tile");
    // {r8}
    real.def(
        // the name of the function
        "abs",
        // the handler
        &qed::nisar::real::abs<heapgrid_t<double>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of a double tile");

    // {r4}
    real.def(
        // the name of the function
        "unwrapped",
        // the handler
        &qed::nisar::real::unwrapped<heapgrid_t<float>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a, "brightness"_a,
        // the docstring
        "render the absolute value of a float tile");
    // {r8}
    real.def(
        // the name of the function
        "unwrapped",
        // the handler
        &qed::nisar::real::unwrapped<heapgrid_t<double>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a, "brightness"_a,
        // the docstring
        "render the absolute value of a double tile");

    // all done
    return;
}


// end of file
