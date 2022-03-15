// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_py_datasets_profile_h)
#define qed_py_datasets_profile_h


// decorators
namespace qed::py::datasets {
    // type aliases
    using values_t = py::tuple;

    // profile for a complex grid source
    template <typename sourceT>
    auto profileGrid(
        // the source
        const sourceT & source,
        // the points
        py::sequence) -> values_t;

    // profile for a complex HDF5 source
    template <typename sourceT>
    auto profileHDF5(
        // the source
        const dataset_t & source,
        // the points
        py::sequence) -> values_t;
}


// pull in the implementations
#define qed_py_datasets_profile_icc
#include "profile.icc"
#undef qed_py_datasets_profile_icc

#endif

// end of file
