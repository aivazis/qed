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


// the phase tile generator
namespace qed::isce2::interferogram::channels {
    // the tile generator for the phase of a complex grid source
    template <typename sourceT>
    inline auto phase(
        // the source
        const sourceT & source,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the stride
        typename sourceT::index_type stride,
        // the hue interval
        double low, double high,
        // the range of values to render
        double brightness) -> bmp_t;
}


// pull in the implementations
#include "phase.icc"

// end of file
