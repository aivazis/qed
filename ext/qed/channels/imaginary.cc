// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"
// the imaginary channel
#include "imaginary.h"


// imaginary
void
qed::py::channels::imaginary(py::module & m)
{
    // bindings for {mapgrid_t} sources
    // add the bindings for {c8}
    m.def(
        // the name of the function
        "imaginaryComplexFloatGrid",
        // the handler
        &imaginaryGridTile<mapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the imaginary part a complex float tile");
    // and the bindings for {c16}
    m.def(
        // the name of the function
        "imaginaryComplexDoubleGrid",
        // the handler
        &imaginaryGridTile<mapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the imaginary part of a complex double tile");

    // bindings for HDF5 sources
    // add the bindings for {c8}
    m.def(
        // the name of the function
        "imaginaryComplexFloatHDF5",
        // the handler
        &imaginaryHDF5Tile<heapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the imaginary part a complex float tile");
    // and the bindings for {c16}
    m.def(
        // the name of the function
        "imaginaryComplexDoubleHDF5",
        // the handler
        &imaginaryHDF5Tile<heapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the imaginary part of a complex double tile");

    // all done
    return;
}


// end of file
