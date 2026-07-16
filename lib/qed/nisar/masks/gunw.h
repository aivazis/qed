// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once


// the GUNW mask tile generator
namespace qed::nisar::masks {
    // renderers
    template <class sourceT>
    class GUNWMask;

    // the tile generator for the mask of a GUNW product
    template <typename sourceT>
    inline auto gunw(
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
#include "gunw.icc"


// end of file
