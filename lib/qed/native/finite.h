// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// external dependencies and the local type aliases
#include "externals.h"
// the namespace and its forward declarations
#include "forward.h"


// the cells of a raster that carry no measurement
namespace qed::native {
    // set the cells of {region} whose parts are not finite numbers to zero, in place; products
    // mark the samples they have nothing to say about that way, and a single one would turn
    // every frequency of a transform into one too
    template <typename gridT>
    inline auto zeroNonFinite(gridT & region) -> void;
} // namespace qed::native


// pull in the implementation
#include "finite.icc"


// end of file
