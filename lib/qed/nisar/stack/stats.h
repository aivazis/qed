// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// the hdf5 handles and the {native::stats_t} return type
#include "../externals.h"


// mean-power statistics over a stack
namespace qed::nisar::stack {
    // sample the per-pixel mean power, mean(|z|^2), over a stack and report its (low, mean, high)
    template <typename sourceT>
    auto stats(
        // the member datasets, one per stack entry
        const std::vector<dataset_t> & datasets,
        // how the cells are laid out on disk
        const datatype_t & datatype,
        // where the sample tile starts
        typename sourceT::index_type origin,
        // how big the sample tile is
        typename sourceT::shape_type tile) -> native::stats_t;
}


// the implementations
#include "stats.icc"


// end of file
