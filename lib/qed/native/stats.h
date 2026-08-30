// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once


// decorators
namespace qed::native {
    // the layout of the collected statistics
    using stats_t = std::tuple<double, double, double>;
    // the layout of a mergeable statistical sample: count, min, mean, m2, max; samples from
    // different tiles combine with the parallel form of Welford's update, so workers can
    // contribute partial results that accumulate into whole-dataset statistics
    using sample_t = std::tuple<double, double, double, double, double>;

    // the magnitude of one cell, whatever kind of number it holds; a raster may be complex,
    // signed, or unsigned, and the reduction to a display value has to mean the same thing
    // in all three cases
    template <typename cellT>
    auto magnitude(const cellT & value) -> double;

    // stats for a complex grid source
    template <typename sourceT>
    auto stats(
        // the source
        const sourceT & source,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile) -> stats_t;

    // the helper that collects the statistics
    template <typename sourceT>
    auto collectStatistics(const sourceT & source) -> stats_t;

    // a mergeable sample of the magnitudes of a strided tile; {origin} and {tile} are in
    // decimated coordinates, exactly as the render kernels see them
    template <typename sourceT>
    auto sample(
        // the source
        const sourceT & source,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the strides
        typename sourceT::index_type stride) -> sample_t;
}


// pull in the implementations
#include "stats.icc"


// end of file
