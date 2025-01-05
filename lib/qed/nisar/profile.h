// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved

// code guard
#pragma once


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
        const native::points_t &,
        // the closed path indicator
        bool closed = false) -> native::values_t<typename sourceT::value_type>;
}


// pull in the implementations
#include "profile.icc"

// end of file
