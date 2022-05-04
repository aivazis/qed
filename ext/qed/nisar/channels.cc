// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for the nisar tile generators
void
qed::py::nisar::channels(py::module & m)
{
    // create a {channels} submodule
    auto channels = m.def_submodule(
        // the name of the module
        "channels",
        // its docstring
        "support for nisar {channels}");

    // {c8} amplitude
    channels.def(
        // the name of the function
        "amplitude",
        // the handler
        &qed::nisar::channels::amplitude<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex float tile");
    // {c16} amplitude
    channels.def(
        // the name of the function
        "amplitude",
        // the handler
        &qed::nisar::channels::amplitude<heapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex double tile");

    // {c8}
    channels.def(
        // the name of the function
        "complex",
        // the handler
        &qed::nisar::channels::complex<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a, "minPhase"_a,
        "maxPhase"_a, "saturation"_a,
        // the docstring
        "render the value of a complex float tile");
    // {c16}
    channels.def(
        // the name of the function
        "complex",
        // the handler
        &qed::nisar::channels::complex<heapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a, "minPhase"_a,
        "maxPhase"_a, "saturation"_a,
        // the docstring
        "render the value of a complex double tile");

    // imaginary part of {c8}
    channels.def(
        // the name of the function
        "imaginary",
        // the handler
        &qed::nisar::channels::imaginary<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the imaginary part a complex float tile");
    // imaginary part of {c16}
    channels.def(
        // the name of the function
        "imaginary",
        // the handler
        &qed::nisar::channels::imaginary<heapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the imaginary part of a complex double tile");

    // phase of {c8}
    channels.def(
        // the name of the function
        "phase",
        // the handler
        &qed::nisar::channels::phase<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "low"_a, "high"_a,
        "saturation"_a, "brightness"_a,
        // the docstring
        "render the phase of a complex float tile");
    // phase of {c16}
    channels.def(
        // the name of the function
        "phase",
        // the handler
        &qed::nisar::channels::phase<heapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "low"_a, "high"_a,
        "saturation"_a, "brightness"_a,
        // the docstring
        "render the phase of a complex double tile");

    // real part of {c8}
    channels.def(
        // the name of the function
        "real",
        // the handler
        &qed::nisar::channels::real<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the real part a complex float tile");
    // real part of {c16}
    channels.def(
        // the name of the function
        "real",
        // the handler
        &qed::nisar::channels::real<heapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "datatype"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the real part of a complex double tile");

    // all done
    return;
}


// end of file
