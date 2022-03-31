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
    // the set of points
    using points_t = std::vector<std::tuple<int, int>>;

    // the table of values
    template <typename valueT>
    using values_t = std::vector<std::tuple<int, int, valueT>>;


    // profile for a complex grid source
    template <typename sourceT>
    auto profileGrid(
        // the source
        const sourceT & source,
        // the points
        const points_t &) -> values_t<typename sourceT::value_type>;

    // profile for a complex HDF5 source
    template <typename sourceT>
    auto profileHDF5(
        // the source
        const dataset_t & source,
        // the data layout
        const datatype_t & datatype,
        // the points
        const points_t &) -> values_t<typename sourceT::value_type>;
}


// pull in the implementations
#define qed_py_datasets_profile_icc
#include "profile.icc"
#undef qed_py_datasets_profile_icc

#endif

// end of file
