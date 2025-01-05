// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved

// code guard
#if !defined(qed_native_channels_complex_h)
#define qed_native_channels_complex_h


// the complex tile generator
namespace qed::native::channels {
    // the tile generator for the complex of a complex grid source
    template <typename sourceT>
    inline auto complex(
        // the source
        const sourceT & source,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the stride
        typename sourceT::index_type stride,
        // the range of values to render
        double min, double max, double phaseMin, double phaseMax, double saturation) -> bmp_t;
}


// pull in the implementations
#define qed_native_channels_complex_icc
#include "complex.icc"
#undef qed_native_channels_complex_icc

#endif

// end of file
