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
    // layouts
    using layout_t = pyre::grid::canonical_t<2>;
    // grids
    template <typename cellT>
    using heapgrid_t = pyre::grid::grid_t<layout_t, heap_t<cellT>>;
    template <typename cellT>
    using mapgrid_t = pyre::grid::grid_t<layout_t, map_t<cellT>>;

    // from {pyre::viz}
    // encodings
    using bmp_t = pyre::viz::bmp_t;

    // color maps
    // complex values
    template <typename sourceT>
    using complex_t = pyre::viz::colormaps::complex_t<sourceT>;
    // grayscale
    template <typename sourceT>
    using gray_t = pyre::viz::colormaps::gray_t<sourceT>;
    // hsb
    template <typename hueSourceT, typename saturationSourceT, typename brightnessSourceT>
    using hsb_t = pyre::viz::colormaps::hsb_t<hueSourceT, saturationSourceT, brightnessSourceT>;
    // hsl
    template <typename hueSourceT, typename saturationSourceT, typename luminositySourceT>
    using hsl_t = pyre::viz::colormaps::hsl_t<hueSourceT, saturationSourceT, luminositySourceT>;

    // filters
    // the amplitude of a complex source
    template <typename sourceT>
    using amplitude_t = pyre::viz::filters::amplitude_t<sourceT>;
    // a supplier of a constant value
    using constant_t = pyre::viz::filters::constant_t<double>;
    // support for zooming
    template <typename sourceT>
    using decimate_t = pyre::viz::filters::decimate_t<sourceT>;
    // extract the imaginary of a complex source
    template <typename sourceT>
    using imaginary_t = pyre::viz::filters::imaginary_t<sourceT>;
    // map a range of values to the unit interval
    template <typename sourceT>
    using parametric_t = pyre::viz::filters::parametric_t<sourceT>;
    // extract the phase of a complex source
    template <typename sourceT>
    using phase_t = pyre::viz::filters::phase_t<sourceT>;
    // extract the real of a complex source
    template <typename sourceT>
    using real_t = pyre::viz::filters::real_t<sourceT>;
}


#endif

// end of file
