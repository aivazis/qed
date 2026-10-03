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


// the spectrum of a region of a complex source
namespace qed::nisar::slc {
    // the longest a region may be along either axis; a region that fits is read in one go and
    // transformed in memory, so this bounds both the read and the transform
    constexpr long fftLimit = 2048;

    // read the region at {origin}+{shape} of a complex source at full resolution, transform
    // it, and render its spectrum as a gray tile of the same shape, with the {range} decibels
    // below the strongest frequency spanning the gray scale; {sourceT} is the grid the region
    // is gathered into, {rasterT} where it is gathered from
    template <typename sourceT, typename rasterT>
    inline auto fft(
        // the source
        const rasterT & dataset,
        // the data layout
        const datatype_t & datatype,
        // the origin of the region
        typename sourceT::index_type origin,
        // the shape of the region
        typename sourceT::shape_type shape,
        // the decibels below the peak that span the gray scale
        double range) -> bmp_t;
} // namespace qed::nisar::slc


// pull in the implementation
#include "fft.icc"


// end of file
