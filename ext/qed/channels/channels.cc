// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// the channels
#include "amplitude.h"
#include "complex.h"
#include "phase.h"


// wrappers over {pyre::memory::map} template expansions
// build the submodule
void
qed::py::channels::channels(py::module & m)
{
    // create a {channels} submodule
    auto channels = m.def_submodule(
        // the name of the module
        "channels",
        // its docstring
        "support for predefined {channels}");

    // add the supported channels
    amplitude(channels);
    complex(channels);
    imaginary(channels);
    phase(channels);
    real(channels);

    // all done
    return;
}


// amplitude
void
qed::py::channels::amplitude(py::module & m)
{
    // add the bindings for {c8}
    m.def(
        // the name of the function
        "amplitudeComplexFloat",
        // the handler
        &amplitudeTile<source_t<std::complex<float>>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex float tile");

    // and the bindings for {c16}
    m.def(
        // the name of the function
        "amplitudeComplexDouble",
        // the handler
        &amplitudeTile<source_t<std::complex<double>>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex double tile");

    // all done
    return;
}


// complex
void
qed::py::channels::complex(py::module & m)
{
    // add the bindings for {c8}
    m.def(
        // the name of the function
        "complexComplexFloat",
        // the handler
        &complexTile<source_t<std::complex<float>>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a, "saturation"_a,
        // the docstring
        "render the value of a complex float tile");

    // and the bindings for {c16}
    m.def(
        // the name of the function
        "complexComplexDouble",
        // the handler
        &complexTile<source_t<std::complex<double>>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a, "saturation"_a,
        // the docstring
        "render the value of a complex double tile");

    // all done
    return;
}


// imaginary
void
qed::py::channels::imaginary(py::module & m)
{
    // all done
    return;
}


// phase
void
qed::py::channels::phase(py::module & m)
{
    // add the bindings for {c8}
    m.def(
        // the name of the function
        "phaseComplexFloat",
        // the handler
        &phaseTile<source_t<std::complex<float>>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "saturation"_a, "brightness"_a,
        // the docstring
        "render the phase of a complex float tile");

    // and the bindings for {c16}
    m.def(
        // the name of the function
        "phaseComplexDouble",
        // the handler
        &phaseTile<source_t<std::complex<double>>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "saturation"_a, "brightness"_a,
        // the docstring
        "render the phase of a complex double tile");

    // all done
    return;
}


// real
void
qed::py::channels::real(py::module & m)
{
    // all done
    return;
}


// end of file
