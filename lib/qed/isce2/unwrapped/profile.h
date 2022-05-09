// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_isce2_unwrapped_profile_h)
#define qed_isce2_unwrapped_profile_h


// decorators
namespace qed::isce2::unwrapped {
    // profile for a complex HDF5 source
    template <typename sourceT>
    auto profile(
        // the source
        const sourceT & source,
        // the points
        const native::points_t &) -> native::values_t<typename sourceT::value_type>;
}


// pull in the implementations
#define qed_isce2_unwrapped_profile_icc
#include "profile.icc"
#undef qed_isce2_unwrapped_profile_icc

#endif

// end of file
