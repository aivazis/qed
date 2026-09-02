// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// external dependencies and the local type aliases
#include "../externals.h"
// the namespace and its forward declarations
#include "../forward.h"


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
#include "amplitude.icc"

// end of file
