// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved

// code guard
#if !defined(qed_nisar_real_abs_h)
#define qed_nisar_real_abs_h


// abs tile generator
namespace qed::nisar::real {
    // the tile generator for the abs of a complex HDF5 source
    template <typename sourceT>
    inline auto abs(
        // the source
        const dataset_t & dataset,
        // the data layout
        const datatype_t & datatype,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the stride
        typename sourceT::index_type stride,
        // the range of values to render
        double min, double max) -> bmp_t;
}


// pull in the implementations
#define qed_nisar_real_abs_icc
#include "abs.icc"
#undef qed_nisar_real_abs_icc

#endif

// end of file
