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


// the taper of a raster
namespace qed::native {
    // taper the cells of {region} smoothly to zero towards its edges, in place, with the two
    // dimensional hann window, the product of a raised cosine along each axis; an axis one cell
    // long is left alone
    template <typename gridT>
    inline auto hann(gridT & region) -> void;
} // namespace qed::native


// pull in the implementation
#include "hann.icc"


// end of file
