// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved

// code guard
#pragma once


// decorators
namespace qed::native {
    // the layout of the collected statistics
    using stats_t = std::tuple<double, double, double>;

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
}


// pull in the implementations
#include "stats.icc"


// end of file
