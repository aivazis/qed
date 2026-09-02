// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// external dependencies and the local type aliases
#include "externals.h"
// the namespace and its forward declarations
#include "forward.h"


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

    // profile for a complex HDF5 source
    template <typename sourceT>
    auto profileBFPQ(
        // the source
        const dataset_t & source,
        // the data layout
        const datatype_t & datatype,
        // the BFPQ lookup table
        bfpq_lut_t bfpq,
        // the points
        const native::points_t &,
        // the closed path indicator
        bool closed = false) -> native::values_t<typename sourceT::value_type>;
}


// pull in the implementations
#include "profile.icc"

// end of file
