// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved

// code guard
#pragma once


// the phase tile generator
namespace qed::nisar::bfpq {
    // the tile generator for the phase of a complex HDF5 source
    template <typename sourceT>
    inline auto phase(
        // the source
        const dataset_t & dataset,
        // the data layout
        const datatype_t & datatype,
        // the BFPQ lookup table
        bfpq_lut_t bfpq,
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
