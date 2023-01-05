// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved

// code guard
#if !defined(qed_nisar_profile_h)
#define qed_nisar_profile_h


// decorators
namespace qed::nisar {
    // profile for a complex HDF5 source
    template <typename sourceT>
    auto profile(
        // the source
        const dataset_t & source,
        // the data layout
        const datatype_t & datatype,
        // the points
        const native::points_t &) -> native::values_t<typename sourceT::value_type>;
}


// pull in the implementations
#define qed_nisar_profile_icc
#include "profile.icc"
#undef qed_nisar_profile_icc

#endif

// end of file
