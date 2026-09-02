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


// the phase tile generator
namespace qed::nisar::slc {
    // the tile generator for the phase of a complex HDF5 source
    // {sourceT} is the grid the tile is gathered into; {rasterT} is where it is gathered from,
    // an hdf5 dataset or a level of a pyramid, and a masked render names the raster its mask
    // comes from the same way
    template <typename sourceT, typename rasterT>
    inline auto phase(
        // the source
        const rasterT & dataset,
        // the data layout
        const datatype_t & datatype,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the stride
        typename sourceT::index_type stride,
        // the hue interval
        double low, double high,
        // the range of values to render
        double saturation, double brightness) -> bmp_t;
}


// pull in the implementations
#include "phase.icc"

// end of file
