// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_py_channels_complex_h)
#define qed_py_channels_complex_h


// decorators
namespace qed::py::channels {
    // the tile generator for the complex of a complex grid source
    template <typename sourceT>
    auto complexGridTile(
        // the source
        const sourceT & source,
        // the zoom level
        int zoom,
        // the origin of the tile
        typename sourceT::index_type origin,
        // the tile shape
        typename sourceT::shape_type tile,
        // the range of values to render
        double min, double max, double saturation) -> bmp_t;

    // the tile generator for the complex of a complex HDF5 source
    template <typename sourceT>
    auto complexHDF5Tile(
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
        double min, double max, double saturation) -> bmp_t;
}


// pull in the implementations
#define qed_py_channels_complex_icc
#include "complex.icc"
#undef qed_py_channels_complex_icc

#endif

// end of file
