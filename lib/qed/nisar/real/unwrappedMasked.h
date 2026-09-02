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
// the local forward declarations
#include "forward.h"


// the unwrapped phase tile generator
namespace qed::nisar::real {
    // the tile generator for datasets that are unwrapped phases
    // {sourceT} is the grid the tile is gathered into; {rasterT} is where it is gathered from,
    // an hdf5 dataset or a level of a pyramid, and a masked render names the raster its mask
    // comes from the same way
    template <typename sourceT, typename rasterT, typename maskRasterT>
    inline auto unwrappedMasked(
        // the source
        const rasterT & source,
        // the mask
        const maskRasterT & mask,
        // the data layout
        const datatype_t & datatype,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the stride
        typename sourceT::index_type stride,
        // the hue interval
        double min, double max,
        // the range of values to render
        double brightness,
        // the magnitude of the value the product declared as its fill
        double fill) -> bmp_t;
}


// pull in the implementations
#include "unwrappedMasked.icc"


// end of file
