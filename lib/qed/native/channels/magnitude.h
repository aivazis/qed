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


// decorators
namespace qed::native::channels {
    // the tile generator for the magnitude of a grid source
    template <typename sourceT>
    auto magnitude(
        // the source
        const sourceT & source,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the stride
        typename sourceT::index_type stride,
        // the range of magnitudes to render
        double min, double max) -> bmp_t;
}


// the implementations
#include "magnitude.icc"


// end of file
