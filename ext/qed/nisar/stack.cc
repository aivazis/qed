// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for the nisar stack tile generators
void
qed::py::nisar::stack(py::module & m)
{
    // create the {stack} submodule
    auto stack = m.def_submodule(
        // the name of the module
        "stack",
        // its docstring
        "support for aggregate views over stacks of nisar datasets");

    // {c8} mean power
    stack.def(
        // the name of the function
        "meanpower",
        // the handler
        &qed::nisar::stack::meanpower<heapgrid_t<std::complex<float>>>,
        // the signature
        "sources"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the mean power of a stack of complex float tiles");
    // {c16} mean power
    stack.def(
        // the name of the function
        "meanpower",
        // the handler
        &qed::nisar::stack::meanpower<heapgrid_t<std::complex<double>>>,
        // the signature
        "sources"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the mean power of a stack of complex double tiles");

    // {c8} coherence
    stack.def(
        // the name of the function
        "coherence",
        // the handler
        &qed::nisar::stack::coherence<heapgrid_t<std::complex<float>>>,
        // the signature
        "sources"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the coherence of a stack of complex float tiles");
    // {c16} coherence
    stack.def(
        // the name of the function
        "coherence",
        // the handler
        &qed::nisar::stack::coherence<heapgrid_t<std::complex<double>>>,
        // the signature
        "sources"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the coherence of a stack of complex double tiles");

    // {c8} mean-power statistics
    stack.def(
        // the name of the function
        "stats",
        // the handler
        &qed::nisar::stack::stats<heapgrid_t<std::complex<float>>>,
        // the signature
        "sources"_a, "datatype"_a, "origin"_a, "shape"_a,
        // the docstring
        "sample the mean power over a stack of complex float tiles");
    // {c16} mean-power statistics
    stack.def(
        // the name of the function
        "stats",
        // the handler
        &qed::nisar::stack::stats<heapgrid_t<std::complex<double>>>,
        // the signature
        "sources"_a, "datatype"_a, "origin"_a, "shape"_a,
        // the docstring
        "sample the mean power over a stack of complex double tiles");

    // all done
    return;
}


// end of file
