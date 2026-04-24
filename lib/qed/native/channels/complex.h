// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once


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


// the implementations
#include "complex.icc"


// end of file
