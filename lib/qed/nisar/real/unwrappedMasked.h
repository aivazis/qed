// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once


// the unwrapped phase tile generator
namespace qed::nisar::real {
    // the tile generator for datasets that are unwrapped phases
    template <typename sourceT>
    inline auto unwrappedMasked(
        // the source
        const dataset_t & source,
        // the mask
        const dataset_t & mask,
        // the data layout
        const datatype_t & datatype,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the stride
        typename sourceT::index_type stride,
        // the hue interval
        double min, double max,
        // the range of values to render
        double brightness) -> bmp_t;
}


// pull in the implementations
#include "unwrappedMasked.icc"


// end of file
