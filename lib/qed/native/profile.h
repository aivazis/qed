// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved

// code guard
#if !defined(qed_native_profile_h)
#define qed_native_profile_h


// decorators
namespace qed::native {
    // type aliases
    // display coordinates
    using point_t = std::tuple<int, int>;
    // the resulting record that appends the values extracted from  the dataset
    template <class valueT>
    using value_t = std::tuple<int, int, valueT>;

    // the set of points
    using points_t = std::vector<point_t>;
    // the table of values
    template <typename valueT>
    using values_t = std::vector<value_t<valueT>>;


    // profile for a complex grid source
    template <typename sourceT>
    auto profile(
        // the source
        const sourceT & source,
        // the points
        const points_t &) -> values_t<typename sourceT::value_type>;
}


// pull in the implementations
#define qed_native_profile_icc
#include "profile.icc"
#undef qed_native_profile_icc

#endif

// end of file
