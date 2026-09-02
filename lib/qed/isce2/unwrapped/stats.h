// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// external dependencies and the local type aliases
#include "../externals.h"
// the namespace and its forward declarations
#include "../forward.h"


// decorators
namespace qed::isce2::unwrapped {
    // stats for a complex HDF5 source
    template <typename sourceT>
    auto stats(
        // the source
        const sourceT & source,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile) -> native::stats_t;
}


// pull in the implementations
#include "stats.icc"


// end of file
