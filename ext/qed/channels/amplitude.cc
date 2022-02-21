// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"
// amplitude channels
#include "amplitude.h"


// amplitude
void
qed::py::channels::amplitude(py::module & m)
{
    // bindings for {mapgrid_t} sources
    // add the bindings for {c8}
    m.def(
        // the name of the function
        "amplitude",
        // the handler
        &amplitudeGridTile<mapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex float tile");
    // and the bindings for {c16}
    m.def(
        // the name of the function
        "amplitude",
        // the handler
        &amplitudeGridTile<mapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex double tile");

    // bindings for HDF5 sources
    // add the bindings for {c8}
    m.def(
        // the name of the function
        "amplitude",
        // the handler
        &amplitudeHDF5Tile<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex float tile");
    // and the bindings for {c16}
    m.def(
        // the name of the function
        "amplitude",
        // the handler
        &amplitudeHDF5Tile<heapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex double tile");

    // all done
    return;
}


// end of file
