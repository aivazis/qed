// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for the native tile generators
void
qed::py::isce2::unwrapped::channels(py::module & m)
{
    // create a {channels} submodule
    auto channels = m.def_submodule(
        // the name of the module
        "channels",
        // its docstring
        "support for native {channels}");


    // add the individual channel bindings
    // {c8} amplitude
    channels.def(
        // the name of the function
        "amplitude",
        // the handler
        &qed::isce2::unwrapped::channels::amplitude<mapgrid_t<float, 3>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "mean"_a, "scale"_a, "exponent"_a,
        // the docstring
        "render the amplitude of a complex float tile");
    // {c16} amplitude
    channels.def(
        // the name of the function
        "amplitude",
        // the handler
        &qed::isce2::unwrapped::channels::amplitude<mapgrid_t<double, 3>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "mean"_a, "scale"_a, "exponent"_a,
        // the docstring
        "render the amplitude of a complex double tile");

    // {c8}
    channels.def(
        // the name of the function
        "complex",
        // the handler
        &qed::isce2::unwrapped::channels::complex<mapgrid_t<float, 3>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "mean"_a, "scale"_a, "exponent"_a,
        "minPhase"_a, "maxPhase"_a,
        // the docstring
        "render the value of a complex float tile");
    // {c16}
    channels.def(
        // the name of the function
        "complex",
        // the handler
        &qed::isce2::unwrapped::channels::complex<mapgrid_t<double, 3>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "mean"_a, "scale"_a, "exponent"_a,
        "minPhase"_a, "maxPhase"_a,
        // the docstring
        "render the value of a complex double tile");

    // phase of {c8}
    channels.def(
        // the name of the function
        "phase",
        // the handler
        &qed::isce2::unwrapped::channels::phase<mapgrid_t<float, 3>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "low"_a, "high"_a, "brightness"_a,
        // the docstring
        "render the phase of a complex float tile");
    // phase of {c16}
    channels.def(
        // the name of the function
        "phase",
        // the handler
        &qed::isce2::unwrapped::channels::phase<mapgrid_t<double, 3>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "low"_a, "high"_a, "brightness"_a,
        // the docstring
        "render the phase of a complex double tile");


    // all done
    return;
}


// end of file
