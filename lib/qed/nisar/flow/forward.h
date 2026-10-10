// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// the flow nodes that bring the rasters of nisar products into a pipeline
namespace qed::nisar::flow {
    // a raster over a dataset of a product, or over a level of its pyramid
    template <class sourceT, class cellT>
    class Raster;
    // the slicer that reads a window of such a raster into a tile
    template <class rasterT, class tileT>
    class Fetch;
    // recolors the cells with no data
    template <class dataT, class colorT>
    class Absence;
    // recolors the cells a mask flags
    template <class ruleT, class maskT, class colorT>
    class Screen;
    // the colormap that shows a mask by itself
    template <class ruleT, class maskT, class colorT>
    class Palette;
    // the readings of the masks of the products
    class GUNW;
    class GCOV;
} // namespace qed::nisar::flow


// end of file
