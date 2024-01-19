// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// code guard
#if !defined(qed_nisar_real_unwrapped_h)
#define qed_nisar_real_unwrapped_h


// the unwrapped phase tile generator
namespace qed::nisar::real {
    // the tile generator for datasets that are unwrapped phases
    template <typename sourceT>
    inline auto unwrapped(
        // the source
        const dataset_t & source,
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
#define qed_nisar_real_unwrapped_icc
#include "unwrapped.icc"
#undef qed_nisar_real_unwrapped_icc

#endif

// end of file
