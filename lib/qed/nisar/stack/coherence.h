// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// the hdf5 handles, the bitmap type, and the native pipeline i delegate to
#include "../externals.h"


// coherence tile generator
namespace qed::nisar::stack {
    // read the matching tile from every member of a complex stack and render its coherence
    template <typename sourceT>
    inline auto coherence(
        // the member datasets, one per stack entry
        const std::vector<dataset_t> & datasets,
        // how the cells are laid out on disk
        const datatype_t & datatype,
        // where the tile starts
        typename sourceT::index_type origin,
        // how big the tile is
        typename sourceT::shape_type tile,
        // how much to decimate as we zoom out
        typename sourceT::index_type stride,
        // the range of coherence values that maps onto the full color scale
        double min, double max) -> bmp_t;
}


// the implementations
#include "coherence.icc"


// end of file
