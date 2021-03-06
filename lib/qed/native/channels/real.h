// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_native_channels_real_h)
#define qed_native_channels_real_h


// the real part tile generator
namespace qed::native::channels {
    // the tile generator for the real part of a complex grid source
    template <typename sourceT>
    inline auto real(
        // the source
        const sourceT & source,
        // the zoom level
        int zoom,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the range of values to render
        double min, double max) -> bmp_t;
}


// pull in the implementations
#define qed_native_channels_real_icc
#include "real.icc"
#undef qed_native_channels_real_icc

#endif

// end of file
