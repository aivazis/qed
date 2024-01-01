// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// code guard
#if !defined(qed_nisar_stats_h)
#define qed_nisar_stats_h


// decorators
namespace qed::nisar {
    // stats for a complex HDF5 source
    template <typename sourceT>
    auto stats(
        // the source
        const dataset_t & source,
        // the data layout
        const datatype_t & datatype,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile) -> native::stats_t;
}


// pull in the implementations
#define qed_nisar_stats_icc
#include "stats.icc"
#undef qed_nisar_stats_icc

#endif

// end of file
