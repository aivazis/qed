// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for the unwrapped tile generators
void
qed::py::isce2::unwrapped::channels(py::module & m)
{
    // create a {channels} submodule
    auto channels = m.def_submodule(
        // the name of the module
        "channels",
        // its docstring
        "support for unwrapped {channels}");

    // every source arrives as a buffer — pyre's type-erased grid, or anything else that speaks the
    // buffer protocol — so one wrapper per channel rebuilds a read-only rank-3 grid over it and
    // dispatches on its cell type

    // render the amplitude of a tile
    channels.def(
        // the name
        "amplitude",
        // the handler
        [](const py::buffer & source, const py::iterable & origin,
           const py::iterable & shape, const py::iterable & stride, double mean,
           double scale, double exponent) -> bmp_t {
            // rebuild the tile geometry as rank-3 grid coordinates
            auto o = asIndex<3>(origin);
            auto t = asShape<3>(shape);
            auto s = asIndex<3>(stride);
            // dispatch on the buffer's cell type and run the kernel over the matching grid
            return onGrid<3, float, double>(source, [&](const auto & grid) {
                return qed::isce2::unwrapped::channels::amplitude(
                    grid, o, t, s, mean, scale, exponent);
            });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "mean"_a, "scale"_a, "exponent"_a,
        // the docstring
        "render the amplitude of a tile");

    // render the value of a tile
    channels.def(
        // the name
        "complex",
        // the handler
        [](const py::buffer & source, const py::iterable & origin,
           const py::iterable & shape, const py::iterable & stride, double mean,
           double scale, double exponent, double minPhase, double maxPhase) -> bmp_t {
            // rebuild the tile geometry as rank-3 grid coordinates
            auto o = asIndex<3>(origin);
            auto t = asShape<3>(shape);
            auto s = asIndex<3>(stride);
            // dispatch on the buffer's cell type and run the kernel over the matching grid
            return onGrid<3, float, double>(source, [&](const auto & grid) {
                return qed::isce2::unwrapped::channels::complex(
                    grid, o, t, s, mean, scale, exponent, minPhase, maxPhase);
            });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "mean"_a, "scale"_a, "exponent"_a,
        "minPhase"_a, "maxPhase"_a,
        // the docstring
        "render the value of a tile");

    // render the phase of a tile
    channels.def(
        // the name
        "phase",
        // the handler
        [](const py::buffer & source, const py::iterable & origin,
           const py::iterable & shape, const py::iterable & stride, double low,
           double high, double brightness) -> bmp_t {
            // rebuild the tile geometry as rank-3 grid coordinates
            auto o = asIndex<3>(origin);
            auto t = asShape<3>(shape);
            auto s = asIndex<3>(stride);
            // dispatch on the buffer's cell type and run the kernel over the matching grid
            return onGrid<3, float, double>(source, [&](const auto & grid) {
                return qed::isce2::unwrapped::channels::phase(grid, o, t, s, low, high, brightness);
            });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "low"_a, "high"_a, "brightness"_a,
        // the docstring
        "render the phase of a tile");

    // all done
    return;
}


// end of file
