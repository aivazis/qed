// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for the native tile generators
void
qed::py::native::channels(py::module & m)
{
    // create a {channels} submodule
    auto channels = m.def_submodule(
        // the name of the module
        "channels",
        // its docstring
        "support for native {channels}");

    // every source arrives as a buffer — pyre's type-erased grid, or anything else that speaks the
    // buffer protocol — so one wrapper per channel rebuilds a read-only rank-2 grid over it and
    // dispatches on its cell type, standing in for the old per-cell-type overload pile

    // render the value of a real tile
    channels.def(
        // the name
        "value",
        // the handler
        [](const py::buffer & source, const py::iterable & origin,
           const py::iterable & shape, const py::iterable & stride, double min,
           double max) -> bmp_t {
            // rebuild the tile geometry as rank-2 grid coordinates
            auto o = asIndex<2>(origin);
            auto t = asShape<2>(shape);
            auto s = asIndex<2>(stride);
            // dispatch on the buffer's cell type and run the kernel over the matching grid
            return onGrid<2, char, int16_t, int32_t, int64_t, float, double>(
                source, [&](const auto & grid) {
                    return qed::native::channels::value(grid, o, t, s, min, max);
                });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the value of a real tile");

    // render the absolute value of a real tile
    channels.def(
        // the name
        "abs",
        // the handler
        [](const py::buffer & source, const py::iterable & origin,
           const py::iterable & shape, const py::iterable & stride, double min,
           double max) -> bmp_t {
            // rebuild the tile geometry as rank-2 grid coordinates
            auto o = asIndex<2>(origin);
            auto t = asShape<2>(shape);
            auto s = asIndex<2>(stride);
            // dispatch on the buffer's cell type and run the kernel over the matching grid
            return onGrid<2, char, int16_t, int32_t, int64_t, float, double>(
                source, [&](const auto & grid) {
                    return qed::native::channels::magnitude(grid, o, t, s, min, max);
                });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of a real tile");

    // render the value of a numpy array directly, without going through a grid
    channels.def(
        // the name
        "value",
        // the handler
        [](py::array_t<float, py::array::c_style | py::array::forcecast> source,
           const py::iterable & shape, float low, float high) -> bmp_t {
            // the normalizer maps a range of values to the unit interval
            using norm_t = parametric_t<const float *>;
            // and the color map turns that into gray
            using colormap_t = gray_t<norm_t>;
            // get the array's data buffer
            auto buffer = static_cast<const float *>(source.request().ptr);
            // map it to the unit interval
            auto norm = norm_t(buffer, norm_t::interval_type(low, high));
            // generate the color
            auto colormap = colormap_t(norm);
            // realize the requested shape as rank-2 grid extents
            auto s = asShape<2>(shape);
            // make a bitmap of that shape
            bmp_t bmp(s[0], s[1]);
            // render into it
            bmp.encode(colormap);
            // and hand it back
            return bmp;
        },
        // the signature
        "source"_a, "shape"_a, "low"_a, "high"_a,
        // the docstring
        "render the values of a numpy array");

    // render the value of a complex tile
    channels.def(
        // the name
        "complex",
        // the handler
        [](const py::buffer & source, const py::iterable & origin,
           const py::iterable & shape, const py::iterable & stride, double min,
           double max, double minPhase, double maxPhase, double saturation) -> bmp_t {
            // rebuild the tile geometry as rank-2 grid coordinates
            auto o = asIndex<2>(origin);
            auto t = asShape<2>(shape);
            auto s = asIndex<2>(stride);
            // dispatch on the buffer's cell type and run the kernel over the matching grid
            return onGrid<2, std::complex<float>, std::complex<double>>(
                source, [&](const auto & grid) {
                    return qed::native::channels::complex(
                        grid, o, t, s, min, max, minPhase, maxPhase, saturation);
                });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a, "minPhase"_a, "maxPhase"_a,
        "saturation"_a,
        // the docstring
        "render the value of a complex tile");

    // render the amplitude of a complex tile
    channels.def(
        // the name
        "amplitude",
        // the handler
        [](const py::buffer & source, const py::iterable & origin,
           const py::iterable & shape, const py::iterable & stride, double min,
           double max) -> bmp_t {
            // rebuild the tile geometry as rank-2 grid coordinates
            auto o = asIndex<2>(origin);
            auto t = asShape<2>(shape);
            auto s = asIndex<2>(stride);
            // dispatch on the buffer's cell type and run the kernel over the matching grid
            return onGrid<2, std::complex<float>, std::complex<double>>(
                source, [&](const auto & grid) {
                    return qed::native::channels::amplitude(grid, o, t, s, min, max);
                });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex tile");

    // render the phase of a complex tile
    channels.def(
        // the name
        "phase",
        // the handler
        [](const py::buffer & source, const py::iterable & origin,
           const py::iterable & shape, const py::iterable & stride, double low,
           double high, double saturation, double brightness) -> bmp_t {
            // rebuild the tile geometry as rank-2 grid coordinates
            auto o = asIndex<2>(origin);
            auto t = asShape<2>(shape);
            auto s = asIndex<2>(stride);
            // dispatch on the buffer's cell type and run the kernel over the matching grid
            return onGrid<2, std::complex<float>, std::complex<double>>(
                source, [&](const auto & grid) {
                    return qed::native::channels::phase(grid, o, t, s, low, high, saturation, brightness);
                });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "low"_a, "high"_a, "saturation"_a,
        "brightness"_a,
        // the docstring
        "render the phase of a complex tile");

    // render the real part of a complex tile
    channels.def(
        // the name
        "real",
        // the handler
        [](const py::buffer & source, const py::iterable & origin,
           const py::iterable & shape, const py::iterable & stride, double min,
           double max) -> bmp_t {
            // rebuild the tile geometry as rank-2 grid coordinates
            auto o = asIndex<2>(origin);
            auto t = asShape<2>(shape);
            auto s = asIndex<2>(stride);
            // dispatch on the buffer's cell type and run the kernel over the matching grid
            return onGrid<2, std::complex<float>, std::complex<double>>(
                source, [&](const auto & grid) {
                    return qed::native::channels::real(grid, o, t, s, min, max);
                });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the real part of a complex tile");

    // render the imaginary part of a complex tile
    channels.def(
        // the name
        "imaginary",
        // the handler
        [](const py::buffer & source, const py::iterable & origin,
           const py::iterable & shape, const py::iterable & stride, double min,
           double max) -> bmp_t {
            // rebuild the tile geometry as rank-2 grid coordinates
            auto o = asIndex<2>(origin);
            auto t = asShape<2>(shape);
            auto s = asIndex<2>(stride);
            // dispatch on the buffer's cell type and run the kernel over the matching grid
            return onGrid<2, std::complex<float>, std::complex<double>>(
                source, [&](const auto & grid) {
                    return qed::native::channels::imaginary(grid, o, t, s, min, max);
                });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the imaginary part of a complex tile");

    // all done
    return;
}


// end of file
