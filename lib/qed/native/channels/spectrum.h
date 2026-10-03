// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// external dependencies and the local type aliases
#include "../externals.h"
// the namespace and its forward declarations
#include "../forward.h"


// the picture of a spectrum
namespace qed::native::channels {
    // render the frequencies in {spectrum}, zero frequency first, as a gray tile of the same
    // shape: zero frequency moves to the center, each cell shows the power of its frequency in
    // decibels, and the {range} decibels below the strongest one span the gray scale
    template <typename sourceT>
    inline auto spectrum(const sourceT & spectrum, double range) -> bmp_t;
} // namespace qed::native::channels


// pull in the implementation
#include "spectrum.icc"


// end of file
