// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// code guard
#pragma once


// decorators
namespace qed::native {
    // type aliases
    // display coordinates
    using point_t = std::tuple<int, int>;
    // line segments
    using segment_t = std::tuple<point_t, point_t>;
    // the resulting record that appends the values extracted from  the dataset
    template <class valueT>
    using value_t = std::tuple<int, int, valueT>;

    // containers of points
    using points_t = std::vector<point_t>;
    // containers of segments
    using segments_t = std::vector<segment_t>;
    // the table of values
    template <typename valueT>
    using values_t = std::vector<value_t<valueT>>;


    // profile for a complex grid source
    template <typename sourceT>
    auto profile(
        // the source
        const sourceT & source,
        // the points
        const points_t &,
        // the closed flag
        bool closed = false) -> values_t<typename sourceT::value_type>;
}


// pull in the implementations
#include "profile.icc"


// end of file
