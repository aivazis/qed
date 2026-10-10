// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// the local forward declarations
#include "forward.h"


// the published names
namespace qed::nisar::flow {
    // a raster of {cellT} over a dataset of a product, or over a level of its pyramid
    template <class sourceT, class cellT>
    using raster_t = Raster<sourceT, cellT>;
    // the slicer that reads a window of a raster into a tile
    template <class rasterT, class tileT>
    using fetch_t = Fetch<rasterT, tileT>;
} // namespace qed::nisar::flow


// end of file
