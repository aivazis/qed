// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// code guard
#if !defined(qed_native_channels_imaginary_h)
#define qed_native_channels_imaginary_h


// the imaginary part tile generator
namespace qed::native::channels {
    // the tile generator for the imaginary part of a complex grid source
    template <typename sourceT>
    inline auto imaginary(
        // the source
        const sourceT & source,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the stride
        typename sourceT::index_type stride,
        // the range of values to render
        double min, double max) -> bmp_t;
}


// pull in the implementations
#define qed_native_channels_imaginary_icc
#include "imaginary.icc"
#undef qed_native_channels_imaginary_icc

#endif

// end of file
