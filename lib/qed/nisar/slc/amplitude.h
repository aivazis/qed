// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved

// code guard
#if !defined(qed_nisar_slc_amplitude_h)
#define qed_nisar_slc_amplitude_h


// amplitude tile generator
namespace qed::nisar::slc {
    // the tile generator for the amplitude of a complex HDF5 source
    template <typename sourceT>
    inline auto amplitude(
        // the source
        const dataset_t & dataset,
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
#define qed_nisar_slc_amplitude_icc
#include "amplitude.icc"
#undef qed_nisar_slc_amplitude_icc

#endif

// end of file
