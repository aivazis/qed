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

    // a mergeable sample of a strided tile of a complex HDF5 source; {origin} and {tile} are
    // in decimated coordinates, exactly as the render kernels see them
    template <typename sourceT>
    auto sample(
        // the source
        const dataset_t & source,
        // the data layout
        const datatype_t & datatype,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the strides
        typename sourceT::index_type stride) -> native::sample_t;

    // a mergeable sample of a strided tile of a BFPQ encoded complex HDF5 source
    template <typename sourceT>
    auto sampleBFPQ(
        // the source
        const dataset_t & source,
        // the data layout
        const datatype_t & datatype,
        // the BFPQ lookup table
        bfpq_lut_t bfpq,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the strides
        typename sourceT::index_type stride) -> native::sample_t;
}


// pull in the implementations
#include "stats.icc"


// end of file
