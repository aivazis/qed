// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// code guard
#if !defined(qed_native_channels_magnitude_h)
#define qed_native_channels_magnitude_h


// decorators
namespace qed::native::channels {
    // the tile generator for the magnitude of a grid source
    template <typename sourceT>
    auto magnitude(
        // the source
        const sourceT & source,
        // the zoom level
        int zoom,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the range of magnitudes to render
        double min, double max) -> bmp_t;
}


// pull in the implementations
#define qed_native_channels_magnitude_icc
#include "magnitude.icc"
#undef qed_native_channels_magnitude_icc

#endif

// end of file
