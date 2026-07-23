// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for the interferogram tile generators
void
qed::py::isce2::interferogram::channels(py::module & m)
{
    // create a {channels} submodule
    auto channels = m.def_submodule(
        // the name of the module
        "channels",
        // its docstring
        "support for interferogram {channels}");

    // every source arrives as a buffer — pyre's type-erased grid, or anything else that speaks the
    // buffer protocol — so one wrapper per channel rebuilds a read-only rank-2 grid over it and
    // dispatches on its cell type

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
                    return qed::isce2::interferogram::channels::amplitude(grid, o, t, s, min, max);
                });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex tile");

    // render the value of a complex tile
    channels.def(
        // the name
        "complex",
        // the handler
        [](const py::buffer & source, const py::iterable & origin,
           const py::iterable & shape, const py::iterable & stride, double min,
           double max, double minPhase, double maxPhase) -> bmp_t {
            // rebuild the tile geometry as rank-2 grid coordinates
            auto o = asIndex<2>(origin);
            auto t = asShape<2>(shape);
            auto s = asIndex<2>(stride);
            // dispatch on the buffer's cell type and run the kernel over the matching grid
            return onGrid<2, std::complex<float>, std::complex<double>>(
                source, [&](const auto & grid) {
                    return qed::isce2::interferogram::channels::complex(
                        grid, o, t, s, min, max, minPhase, maxPhase);
                });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a, "minPhase"_a, "maxPhase"_a,
        // the docstring
        "render the value of a complex tile");

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
                    return qed::isce2::interferogram::channels::imaginary(grid, o, t, s, min, max);
                });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the imaginary part of a complex tile");

    // render the phase of a complex tile
    channels.def(
        // the name
        "phase",
        // the handler
        [](const py::buffer & source, const py::iterable & origin,
           const py::iterable & shape, const py::iterable & stride, double low,
           double high, double brightness) -> bmp_t {
            // rebuild the tile geometry as rank-2 grid coordinates
            auto o = asIndex<2>(origin);
            auto t = asShape<2>(shape);
            auto s = asIndex<2>(stride);
            // dispatch on the buffer's cell type and run the kernel over the matching grid
            return onGrid<2, std::complex<float>, std::complex<double>>(
                source, [&](const auto & grid) {
                    return qed::isce2::interferogram::channels::phase(
                        grid, o, t, s, low, high, brightness);
                });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "low"_a, "high"_a, "brightness"_a,
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
                    return qed::isce2::interferogram::channels::real(grid, o, t, s, min, max);
                });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the real part of a complex tile");

    // all done
    return;
}


// end of file
