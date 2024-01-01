// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// code guard
#if !defined(qed_isce2_unwrapped_channels_phase_h)
#define qed_isce2_unwrapped_channels_phase_h


// the phase tile generator
namespace qed::isce2::unwrapped::channels {
    // the tile generator for the phase of a complex grid source
    template <typename sourceT>
    inline auto phase(
        // the source
        const sourceT & source,
        // the zoom level
        int zoom,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the hue interval
        double low, double high,
        // the range of values to render
        double brightness) -> bmp_t;
}


// pull in the implementations
#define qed_isce2_unwrapped_channels_phase_icc
#include "phase.icc"
#undef qed_isce2_unwrapped_channels_phase_icc

#endif

// end of file
