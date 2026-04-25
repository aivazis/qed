// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once


// the value part tile generator
namespace qed::nisar::mask {
    // renderers
    template <class sourceT>
    class RawMask;

    // the tile generator for the value part of a complex HDF5 source
    template <typename sourceT>
    inline auto raw(
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
#include "raw.icc"


// end of file
