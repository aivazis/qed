// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// code guard
#pragma once


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
