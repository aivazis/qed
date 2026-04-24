// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once


// the phase tile generator
namespace qed::native::channels {
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
        // the hue interaval
        double low, double high,
        // the range of values to render
        double saturation, double brightness) -> bmp_t;
}


// the implementations
#include "phase.icc"


// end of file
