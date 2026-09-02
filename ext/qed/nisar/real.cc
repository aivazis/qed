// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// externals
#include "external.h"
// namespace setup
#include "forward.h"


// the real kernels, bound once per kind of raster they can read
namespace qed::py::nisar {
    // bind the real kernels over a source of type {rasterT} and a mask of type {maskRasterT}
    template <class rasterT, class maskRasterT>
    inline void bindReal(py::module & real)
    {
        // the grid the kernels read into
        using grid_t = heapgrid_t<float>;
        real.def(
            // the name
            "value",
            // the handler
            [](const rasterT & source, const datatype_t & datatype, const py::iterable & origin,
               const py::iterable & shape, const py::iterable & stride, double min,
               double max) -> bmp_t {
                // gather the tile and render it
                return qed::nisar::real::value<grid_t>(
                    source, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride),
                    min, max);
            },
            // the signature
            "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
            // the docstring
            "render the value of a real tile");
        real.def(
            // the name
            "abs",
            // the handler
            [](const rasterT & source, const datatype_t & datatype, const py::iterable & origin,
               const py::iterable & shape, const py::iterable & stride, double min,
               double max) -> bmp_t {
                // gather the tile and render it
                return qed::nisar::real::abs<grid_t>(
                    source, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride),
                    min, max);
            },
            // the signature
            "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
            // the docstring
            "render the absolute value of a real tile");
        real.def(
            // the name
            "coherence",
            // the handler
            [](const rasterT & source, const maskRasterT & mask, const datatype_t & datatype,
               const py::iterable & origin, const py::iterable & shape, const py::iterable & stride,
               double min, double max, double fill) -> bmp_t {
                // gather the tile and render it
                return qed::nisar::real::coherence<grid_t>(
                    source, mask, datatype, asIndex<2>(origin), asShape<2>(shape),
                    asIndex<2>(stride), min, max, fill);
            },
            // the signature
            "source"_a, "mask"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
            "fill"_a,
            // the docstring
            "render the coherence of a real tile");
        real.def(
            // the name
            "coherenceMasked",
            // the handler
            [](const rasterT & source, const maskRasterT & mask, const datatype_t & datatype,
               const py::iterable & origin, const py::iterable & shape, const py::iterable & stride,
               double min, double max, double fill) -> bmp_t {
                // gather the tile and render it
                return qed::nisar::real::coherenceMasked<grid_t>(
                    source, mask, datatype, asIndex<2>(origin), asShape<2>(shape),
                    asIndex<2>(stride), min, max, fill);
            },
            // the signature
            "source"_a, "mask"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
            "fill"_a,
            // the docstring
            "render the coherence of a real tile, masked");
        real.def(
            // the name
            "covariance",
            // the handler
            [](const rasterT & source, const maskRasterT & mask, const datatype_t & datatype,
               const py::iterable & origin, const py::iterable & shape, const py::iterable & stride,
               double min, double max, double fill) -> bmp_t {
                // gather the tile and render it
                return qed::nisar::real::covariance<grid_t>(
                    source, mask, datatype, asIndex<2>(origin), asShape<2>(shape),
                    asIndex<2>(stride), min, max, fill);
            },
            // the signature
            "source"_a, "mask"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
            "fill"_a,
            // the docstring
            "render the covariance of a real tile");
        real.def(
            // the name
            "covarianceMasked",
            // the handler
            [](const rasterT & source, const maskRasterT & mask, const datatype_t & datatype,
               const py::iterable & origin, const py::iterable & shape, const py::iterable & stride,
               double min, double max, double fill) -> bmp_t {
                // gather the tile and render it
                return qed::nisar::real::covarianceMasked<grid_t>(
                    source, mask, datatype, asIndex<2>(origin), asShape<2>(shape),
                    asIndex<2>(stride), min, max, fill);
            },
            // the signature
            "source"_a, "mask"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
            "fill"_a,
            // the docstring
            "render the covariance of a real tile, masked");
        real.def(
            // the name
            "unwrapped",
            // the handler
            [](const rasterT & source, const maskRasterT & mask, const datatype_t & datatype,
               const py::iterable & origin, const py::iterable & shape, const py::iterable & stride,
               double min, double max, double brightness, double fill) -> bmp_t {
                // gather the tile and render it
                return qed::nisar::real::unwrapped<grid_t>(
                    source, mask, datatype, asIndex<2>(origin), asShape<2>(shape),
                    asIndex<2>(stride), min, max, brightness, fill);
            },
            // the signature
            "source"_a, "mask"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
            "brightness"_a, "fill"_a,
            // the docstring
            "render the unwrapped phase of a real tile");
        real.def(
            // the name
            "unwrappedMasked",
            // the handler
            [](const rasterT & source, const maskRasterT & mask, const datatype_t & datatype,
               const py::iterable & origin, const py::iterable & shape, const py::iterable & stride,
               double min, double max, double brightness, double fill) -> bmp_t {
                // gather the tile and render it
                return qed::nisar::real::unwrappedMasked<grid_t>(
                    source, mask, datatype, asIndex<2>(origin), asShape<2>(shape),
                    asIndex<2>(stride), min, max, brightness, fill);
            },
            // the signature
            "source"_a, "mask"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
            "brightness"_a, "fill"_a,
            // the docstring
            "render the unwrapped phase of a real tile, masked");
        // all done
        return;
    }
}    // namespace qed::py::nisar


// real
void
qed::py::nisar::real(py::module & m)
{
    // create the real submodule
    auto real = m.def_submodule(
        // the name of the module
        "real",
        // its docstring
        "support for nisar {real} datasets");
    // the kernels over hdf5 datasets, the way the products are read
    bindReal<dataset_t, dataset_t>(real);
    // and over pyramid levels, the way a zoomed out view is read
    bindReal<level_t<float>, level_t<std::uint8_t>>(real);
    // all done
    return;
}

// end of file
