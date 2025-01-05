// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved

// code guard
#if !defined(qed_nisar_slc_phase_h)
#define qed_nisar_slc_phase_h


// the phase tile generator
namespace qed::nisar::slc {
    // the tile generator for the phase of a complex HDF5 source
    template <typename sourceT>
    inline auto phase(
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
        // the hue interval
        double low, double high,
        // the range of values to render
        double saturation, double brightness) -> bmp_t;
}


// pull in the implementations
#define qed_nisar_slc_phase_icc
#include "phase.icc"
#undef qed_nisar_slc_phase_icc

#endif

// end of file
