// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_py_external_h)
#define qed_py_external_h


// STL
#include <memory>
#include <string>
#include <tuple>

// journal
#include <pyre/journal.h>
// pyre
#include <pyre/h5.h>
#include <pyre/grid.h>
#include <pyre/viz.h>


// pybind support
#include <pybind11/pybind11.h>
#include <pybind11/complex.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>


// type aliases
namespace qed::py {
    // import {pybind11}
    namespace py = pybind11;
    // get the special {pybind11} literals
    using namespace py::literals;

    // sizes of things
    using size_t = std::size_t;
    // strings
    using string_t = std::string;

    // pointer wrappers
    template <class T>
    using unique_pointer = std::unique_ptr<T>;

    // a collection of tile statstics
    using stats_t = std::tuple<double, double, double>;

    // aliases for hdf5 entities
    using dataset_t = pyre::h5::dataset_t;
    using dataspace_t = pyre::h5::dataspace_t;
    using datatype_t = pyre::h5::datatype_t;
}

// type aliases for pyre types
namespace qed::py {
    // from {pyre::memory}
    // storage strategies
    template <typename cellT>
    using heap_t = pyre::memory::heap_t<cellT>;
    template <typename cellT>
    using map_t = pyre::memory::constmap_t<cellT>;

    // from {pyre::grid}
    // grids
    template <typename cellT, int dim = 2>
    using heapgrid_t = pyre::grid::grid_t<pyre::grid::canonical_t<dim>, heap_t<cellT>>;
    template <typename cellT, int dim = 2>
    using mapgrid_t = pyre::grid::grid_t<pyre::grid::canonical_t<dim>, map_t<cellT>>;
}


#endif

// end of file
