// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_isce2_unwrapped_channels_complex_h)
#define qed_isce2_unwrapped_channels_complex_h


// the complex tile generator
namespace qed::isce2::unwrapped::channels {
    // the tile generator for the complex of a complex grid source
    template <typename sourceT>
    inline auto complex(
        // the source
        const sourceT & source,
        // the zoom level
        int zoom,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the range of values to render
        double min, double max, double phaseMin, double phaseMax) -> bmp_t;
}


// pull in the implementations
#define qed_isce2_unwrapped_channels_complex_icc
#include "complex.icc"
#undef qed_isce2_unwrapped_channels_complex_icc

#endif

// end of file
