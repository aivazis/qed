// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// stats
void
qed::py::native::stats(py::module & m)
{
    // bindings for {mapgrid_t} sources
    m.def(
        // the name of the function
        "stats",
        // the handler
        &qed::native::stats<mapgrid_t<char>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a,
        // the docstring
        "collect statistics on a subset of a dataset");

    m.def(
        // the name of the function
        "stats",
        // the handler
        &qed::native::stats<mapgrid_t<int8_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a,
        // the docstring
        "collect statistics on a subset of a dataset");

    m.def(
        // the name of the function
        "stats",
        // the handler
        &qed::native::stats<mapgrid_t<int16_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a,
        // the docstring
        "collect statistics on a subset of a dataset");

    m.def(
        // the name of the function
        "stats",
        // the handler
        &qed::native::stats<mapgrid_t<int32_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a,
        // the docstring
        "collect statistics on a subset of a dataset");

    m.def(
        // the name of the function
        "stats",
        // the handler
        &qed::native::stats<mapgrid_t<int64_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a,
        // the docstring
        "collect statistics on a subset of a dataset");

    m.def(
        // the name of the function
        "stats",
        // the handler
        &qed::native::stats<mapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a,
        // the docstring
        "collect statistics on a subset of a dataset");

    // bindings for {mapgrid_t} sources
    m.def(
        // the name of the function
        "stats",
        // the handler
        &qed::native::stats<mapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a,
        // the docstring
        "collect statistics on a subset of a dataset");

    // all done
    return;
}


// end of file
