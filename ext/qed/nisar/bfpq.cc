// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// the BFPQ lookup table helper
#include "bfpq_lut.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for the nisar BFPQ tile generators
void
qed::py::nisar::bfpq(py::module & m)
{
    // create the {bfpq} submodule
    auto bfpq = m.def_submodule(
        // the name of the module
        "bfpq",
        // its docstring
        "support for BFPQ encoded {slc} datasets");

    // the BFPQ kernels read a tile out of an h5 dataset (using {datatype} for the on-disk layout),
    // decode it through the BFPQ lookup table, and render it; the reader hands the lookup table in
    // as a buffer, which we rebuild into the small heap grid the kernels expect
    using grid_t = heapgrid_t<std::complex<float>>;

    // render the amplitude of a BFPQ encoded slc tile
    bfpq.def(
        // the name
        "amplitude",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype, const py::buffer & lut,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride, double min, double max) -> bmp_t {
            // read and decode the tile, then render it
            return qed::nisar::bfpq::amplitude<grid_t>(
                source, datatype, asBFPQ(lut), asIndex<2>(origin), asShape<2>(shape),
                asIndex<2>(stride), min, max);
        },
        // the signature
        "source"_a, "datatype"_a, "bfpq"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a BFPQ encoded slc tile");

    // render the value of a BFPQ encoded slc tile
    bfpq.def(
        // the name
        "complex",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype, const py::buffer & lut,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride, double min, double max, double minPhase,
           double maxPhase, double saturation) -> bmp_t {
            // read and decode the tile, then render it
            return qed::nisar::bfpq::complex<grid_t>(
                source, datatype, asBFPQ(lut), asIndex<2>(origin), asShape<2>(shape),
                asIndex<2>(stride), min, max, minPhase, maxPhase, saturation);
        },
        // the signature
        "source"_a, "datatype"_a, "bfpq"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        "minPhase"_a, "maxPhase"_a, "saturation"_a,
        // the docstring
        "render the value of a BFPQ encoded slc tile");

    // render the imaginary part of a BFPQ encoded slc tile
    bfpq.def(
        // the name
        "imaginary",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype, const py::buffer & lut,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride, double min, double max) -> bmp_t {
            // read and decode the tile, then render it
            return qed::nisar::bfpq::imaginary<grid_t>(
                source, datatype, asBFPQ(lut), asIndex<2>(origin), asShape<2>(shape),
                asIndex<2>(stride), min, max);
        },
        // the signature
        "source"_a, "datatype"_a, "bfpq"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the imaginary part of a BFPQ encoded slc tile");

    // render the phase of a BFPQ encoded slc tile
    bfpq.def(
        // the name
        "phase",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype, const py::buffer & lut,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride, double low, double high, double saturation,
           double brightness) -> bmp_t {
            // read and decode the tile, then render it
            return qed::nisar::bfpq::phase<grid_t>(
                source, datatype, asBFPQ(lut), asIndex<2>(origin), asShape<2>(shape),
                asIndex<2>(stride), low, high, saturation, brightness);
        },
        // the signature
        "source"_a, "datatype"_a, "bfpq"_a, "origin"_a, "shape"_a, "stride"_a, "low"_a, "high"_a,
        "saturation"_a, "brightness"_a,
        // the docstring
        "render the phase of a BFPQ encoded slc tile");

    // render the real part of a BFPQ encoded slc tile
    bfpq.def(
        // the name
        "real",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype, const py::buffer & lut,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride, double min, double max) -> bmp_t {
            // read and decode the tile, then render it
            return qed::nisar::bfpq::real<grid_t>(
                source, datatype, asBFPQ(lut), asIndex<2>(origin), asShape<2>(shape),
                asIndex<2>(stride), min, max);
        },
        // the signature
        "source"_a, "datatype"_a, "bfpq"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the real part of a BFPQ encoded slc tile");

    // all done
    return;
}


// end of file
