// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for the nisar real tile generators
void
qed::py::nisar::real(py::module & m)
{
    // create the {real} submodule
    auto real = m.def_submodule(
        // the name of the module
        "real",
        // its docstring
        "support for nisar {real} datasets");

    // the nisar kernels read a tile out of an h5 dataset (using {datatype} for the on-disk layout)
    // into a grid of a fixed cell type, then render it; the masked variants pull a second dataset
    // for the mask
    using grid_t = heapgrid_t<float>;

    // render the value of a real tile
    real.def(
        // the name
        "value",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride, double min, double max) -> bmp_t {
            // read the tile and render it
            return qed::nisar::real::value<grid_t>(
                source, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride), min,
                max);
        },
        // the signature
        "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the value of a real tile");

    // render the absolute value of a real tile
    real.def(
        // the name
        "abs",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride, double min, double max) -> bmp_t {
            // read the tile and render it
            return qed::nisar::real::abs<grid_t>(
                source, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride), min,
                max);
        },
        // the signature
        "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of a real tile");

    // render the coherence of a real tile
    real.def(
        // the name
        "coherence",
        // the handler
        [](const dataset_t & source, const dataset_t & mask, const datatype_t & datatype,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride, double min, double max) -> bmp_t {
            // read the tile and its mask and render them
            return qed::nisar::real::coherence<grid_t>(
                source, mask, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride),
                min, max);
        },
        // the signature
        "source"_a, "mask"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the coherence of a real tile");

    // render the coherence of a real tile, masked
    real.def(
        // the name
        "coherenceMasked",
        // the handler
        [](const dataset_t & source, const dataset_t & mask, const datatype_t & datatype,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride, double min, double max) -> bmp_t {
            // read the tile and its mask and render them
            return qed::nisar::real::coherenceMasked<grid_t>(
                source, mask, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride),
                min, max);
        },
        // the signature
        "source"_a, "mask"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the coherence of a real tile, masked");

    // render the covariance of a real tile
    real.def(
        // the name
        "covariance",
        // the handler
        [](const dataset_t & source, const dataset_t & mask, const datatype_t & datatype,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride, double min, double max) -> bmp_t {
            // read the tile and its mask and render them
            return qed::nisar::real::covariance<grid_t>(
                source, mask, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride),
                min, max);
        },
        // the signature
        "source"_a, "mask"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the covariance of a real tile");

    // render the covariance of a real tile, masked
    real.def(
        // the name
        "covarianceMasked",
        // the handler
        [](const dataset_t & source, const dataset_t & mask, const datatype_t & datatype,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride, double min, double max) -> bmp_t {
            // read the tile and its mask and render them
            return qed::nisar::real::covarianceMasked<grid_t>(
                source, mask, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride),
                min, max);
        },
        // the signature
        "source"_a, "mask"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the covariance of a real tile, masked");

    // render the unwrapped phase of a real tile
    real.def(
        // the name
        "unwrapped",
        // the handler
        [](const dataset_t & source, const dataset_t & mask, const datatype_t & datatype,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride, double min, double max, double brightness) -> bmp_t {
            // read the tile and its mask and render them
            return qed::nisar::real::unwrapped<grid_t>(
                source, mask, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride),
                min, max, brightness);
        },
        // the signature
        "source"_a, "mask"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        "brightness"_a,
        // the docstring
        "render the unwrapped phase of a real tile");

    // render the unwrapped phase of a real tile, masked
    real.def(
        // the name
        "unwrappedMasked",
        // the handler
        [](const dataset_t & source, const dataset_t & mask, const datatype_t & datatype,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride, double min, double max, double brightness) -> bmp_t {
            // read the tile and its mask and render them
            return qed::nisar::real::unwrappedMasked<grid_t>(
                source, mask, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride),
                min, max, brightness);
        },
        // the signature
        "source"_a, "mask"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        "brightness"_a,
        // the docstring
        "render the unwrapped phase of a real tile, masked");

    // all done
    return;
}


// end of file
