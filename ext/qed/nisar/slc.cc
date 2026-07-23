// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for the nisar slc tile generators
void
qed::py::nisar::slc(py::module & m)
{
    // create the {slc} submodule
    auto slc = m.def_submodule(
        // the name of the module
        "slc",
        // its docstring
        "support for nisar {slc} datasets");

    // the nisar kernels read a tile out of an h5 dataset (using {datatype} for the on-disk layout)
    // into a grid of a fixed cell type, then render it; the grid type is a compile-time detail, so
    // each wrapper just threads the dataset and layout through and turns the geometry into grid
    // coordinates
    using grid_t = heapgrid_t<std::complex<float>>;

    // render the amplitude of a complex slc tile
    slc.def(
        // the name
        "amplitude",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype,
           const py::iterable & origin, const py::iterable & shape,
           const py::iterable & stride, double min, double max) -> bmp_t {
            // read the tile and render it
            return qed::nisar::slc::amplitude<grid_t>(
                source, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride), min,
                max);
        },
        // the signature
        "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex slc tile");

    // render the value of a complex slc tile
    slc.def(
        // the name
        "complex",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype,
           const py::iterable & origin, const py::iterable & shape,
           const py::iterable & stride, double min, double max, double minPhase,
           double maxPhase, double saturation) -> bmp_t {
            // read the tile and render it
            return qed::nisar::slc::complex<grid_t>(
                source, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride), min,
                max, minPhase, maxPhase, saturation);
        },
        // the signature
        "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a, "minPhase"_a,
        "maxPhase"_a, "saturation"_a,
        // the docstring
        "render the value of a complex slc tile");

    // render the imaginary part of a complex slc tile
    slc.def(
        // the name
        "imaginary",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype,
           const py::iterable & origin, const py::iterable & shape,
           const py::iterable & stride, double min, double max) -> bmp_t {
            // read the tile and render it
            return qed::nisar::slc::imaginary<grid_t>(
                source, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride), min,
                max);
        },
        // the signature
        "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the imaginary part of a complex slc tile");

    // render the phase of a complex slc tile
    slc.def(
        // the name
        "phase",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype,
           const py::iterable & origin, const py::iterable & shape,
           const py::iterable & stride, double low, double high, double saturation,
           double brightness) -> bmp_t {
            // read the tile and render it
            return qed::nisar::slc::phase<grid_t>(
                source, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride), low,
                high, saturation, brightness);
        },
        // the signature
        "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "low"_a, "high"_a,
        "saturation"_a, "brightness"_a,
        // the docstring
        "render the phase of a complex slc tile");

    // render the real part of a complex slc tile
    slc.def(
        // the name
        "real",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype,
           const py::iterable & origin, const py::iterable & shape,
           const py::iterable & stride, double min, double max) -> bmp_t {
            // read the tile and render it
            return qed::nisar::slc::real<grid_t>(
                source, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride), min,
                max);
        },
        // the signature
        "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the real part of a complex slc tile");

    // all done
    return;
}


// end of file
