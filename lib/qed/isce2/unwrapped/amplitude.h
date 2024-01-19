// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// code guard
#if !defined(qed_isce2_unwrapped_channels_amplitude_h)
#define qed_isce2_unwrapped_channels_amplitude_h


// the amplitude tile generator
namespace qed::isce2::unwrapped::channels {
    // the tile generator for the amplitude of a complex grid source
    template <typename sourceT>
    inline auto amplitude(
        // the source
        const sourceT & source,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the strides
        typename sourceT::index_type stride,
        // the range of values to render
        double mean, double scale, double exponent) -> bmp_t;
}


// pull in the implementations
#define qed_isce2_unwrapped_channels_amplitude_icc
#include "amplitude.icc"
#undef qed_isce2_unwrapped_channels_amplitude_icc

#endif

// end of file
