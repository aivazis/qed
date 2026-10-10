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
    // recolors the cells with no data
    template <class dataT, class colorT>
    using absence_t = Absence<dataT, colorT>;
    // recolor the cells the masks of GUNW and GCOV products flag
    template <class maskT, class colorT>
    using gunw_screen_t = Screen<GUNW, maskT, colorT>;
    template <class maskT, class colorT>
    using gcov_screen_t = Screen<GCOV, maskT, colorT>;
    // the colormaps that show the masks of GUNW and GCOV products by themselves
    template <class maskT, class colorT>
    using gunw_palette_t = Palette<GUNW, maskT, colorT>;
    template <class maskT, class colorT>
    using gcov_palette_t = Palette<GCOV, maskT, colorT>;
} // namespace qed::nisar::flow


// end of file
