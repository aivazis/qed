// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for the nisar tile generators
void
qed::py::nisar::bfpq(py::module & m)
{
    // create the {bfpq} submodule
    auto bfpq = m.def_submodule(
        // the name of the module
        "bfpq",
        // its docstring
        "support for BFPQ encoded {slc} datasets");

    // {c8} amplitude
    bfpq.def(
        // the name of the function
        "amplitude",
        // the handler
        &qed::nisar::bfpq::amplitude<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "datatype"_a, "bfpq"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a BFPQ encoded complex float tile");

    // {c8}
    bfpq.def(
        // the name of the function
        "complex",
        // the handler
        &qed::nisar::bfpq::complex<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "datatype"_a, "bfpq"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        "minPhase"_a, "maxPhase"_a, "saturation"_a,
        // the docstring
        "render the value of a BFPQ encoded complex float tile");

    // imaginary part of {c8}
    bfpq.def(
        // the name of the function
        "imaginary",
        // the handler
        &qed::nisar::bfpq::imaginary<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "datatype"_a, "bfpq"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the imaginary part of a BFPQ encoded complex float tile");

    // phase of {c8}
    bfpq.def(
        // the name of the function
        "phase",
        // the handler
        &qed::nisar::bfpq::phase<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "datatype"_a, "bfpq"_a, "origin"_a, "shape"_a, "stride"_a, "low"_a, "high"_a,
        "saturation"_a, "brightness"_a,
        // the docstring
        "render the phase of a BFPQ encoded complex float tile");

    // real part of {c8}
    bfpq.def(
        // the name of the function
        "real",
        // the handler
        &qed::nisar::bfpq::real<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "datatype"_a, "bfpq"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the real part of a BFPQ encoded complex float tile");

    // all done
    return;
}


// end of file
