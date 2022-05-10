// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_isce2_unwrapped_stats_h)
#define qed_isce2_unwrapped_stats_h


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
#define qed_isce2_unwrapped_stats_icc
#include "stats.icc"
#undef qed_isce2_unwrapped_stats_icc

#endif

// end of file
