// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved

// code guard
#if !defined(qed_nisar_slc_real_h)
#define qed_nisar_slc_real_h


// the real part tile generator
namespace qed::nisar::slc {
    // the tile generator for the real part of a complex HDF5 source
    template <typename sourceT>
    inline auto real(
        // the source
        const dataset_t & source,
        // the data layout
        const datatype_t & datatype,
        // the zoom level
        int zoom,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the range of values to render
        double min, double max) -> bmp_t;
}


// pull in the implementations
#define qed_nisar_slc_real_icc
#include "real.icc"
#undef qed_nisar_slc_real_icc

#endif

// end of file
