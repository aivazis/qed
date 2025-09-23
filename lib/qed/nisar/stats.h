// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved

// code guard
#pragma once


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

    // stats for a BFPQ encoded complex HDF5 source
    template <typename sourceT>
    auto statsBFPQ(
        // the source
        const dataset_t & source,
        // the data layout
        const datatype_t & datatype,
        // the BFPQ lookup table
        bfpq_lut_t bfpq,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile) -> native::stats_t;
}


// pull in the implementations
#include "stats.icc"


// end of file
