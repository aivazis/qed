// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// external dependencies and the local type aliases
#include "externals.h"
// the namespace and its forward declarations
#include "forward.h"


// decorators
namespace qed::nisar {
    // build a tile of a pyramid level by decimating the level below it
    //
    // the pyramid exists so that a zoomed out view reads a small dataset at unit stride
    // instead of striding a large one: a strided read of a chunked product touches every
    // chunk its footprint covers, so at stride {s} it decompresses {s}^2 cells for every
    // cell it keeps. decimation here is plain striding, exactly what the render kernels do,
    // so a level built by repeated halving is cell for cell identical to a strided read of
    // the base; that is what lets a pyramid read stand in for the real thing
    //
    // reports a mergeable statistical record of the tile: the decimation has every cell in
    // hand anyway, so the statistics of the level, and through it of the whole raster, are
    // a byproduct rather than a second pass. a tile of pure fill contributes an empty
    // record and is not written at all, so the destination chunk stays unallocated and a
    // sparse product does not become a dense one
    //
    // {sourceT} is the grid the tile passes through; {rasterT} is the level being read, an
    // hdf5 dataset or a level of a pyramid; {draftT} is the level being written, an hdf5
    // dataset or the draft of a pyramid level
    template <typename sourceT, typename rasterT, typename draftT>
    auto decimate(
        // the level being read
        const rasterT & source,
        // the level being written
        draftT & destination,
        // the data layout, shared by both
        const datatype_t & datatype,
        // the origin of the tile, in the coordinates of the destination
        typename sourceT::index_type origin,
        // the shape of the tile, in the coordinates of the destination
        typename sourceT::shape_type tile,
        // the decimation, applied to the source
        typename sourceT::index_type stride) -> native::sample_t;
}


// pull in the implementations
#include "pyramid.icc"


// end of file
