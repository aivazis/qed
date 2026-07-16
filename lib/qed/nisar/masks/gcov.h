// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once


// the GCOV mask tile generator
namespace qed::nisar::masks {
    // renderers
    template <class sourceT>
    class GCOVMask;

    // the tile generator for the mask of a GCOV product
    template <typename sourceT>
    inline auto gcov(
        // the source
        const dataset_t & source,
        // the data layout
        const datatype_t & datatype,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the stride
        typename sourceT::index_type stride) -> bmp_t;
}


// pull in the implementations
#include "gcov.icc"


// end of file
