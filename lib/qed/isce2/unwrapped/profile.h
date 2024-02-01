// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// code guard
#pragma once


// decorators
namespace qed::isce2::unwrapped {
    // type aliases
    // display coordinates
    using point_t = std::tuple<int, int>;
    // a path has a bunch of these
    using points_t = std::vector<point_t>;

    // line segments
    using segment_t = std::tuple<point_t, point_t>;
    // containers of segments
    using segments_t = std::vector<segment_t>;

    // the profile record has the incoming pixel location and my amplitude/phase pair
    template <class valueT>
    using value_t = std::tuple<int, int, valueT, valueT>;
    // the profile
    template <class valueT>
    using values_t = std::vector<value_t<valueT>>;


    // profile for a complex HDF5 source
    template <typename sourceT>
    auto profile(
        // the source
        const sourceT & source,
        // the points
        const points_t &,
        // the closed path indicator
        bool closed = false) -> values_t<typename sourceT::value_type>;
}


// pull in the implementations
#include "profile.icc"


// end of file
