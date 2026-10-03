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


// the discrete fourier transform of a raster
namespace qed::native {
    // the two dimensional transform of the complex cells of {source}, as a fresh grid of the
    // same shape whose cells are the amplitudes of the frequencies, zero frequency first; the
    // {source} is left untouched
    template <typename gridT>
    inline auto fft(const gridT & source) -> gridT;
} // namespace qed::native


// pull in the implementation
#include "fft.icc"


// end of file
