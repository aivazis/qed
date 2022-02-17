// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_py_channels_external_h)
#define qed_py_channels_external_h


// inherit
#include "../external.h"

// pyre
#include <pyre/viz.h>
#include <pyre/grid.h>

// hdf5
#include <H5Cpp.h>


// type aliases
namespace qed::py::channels {
    // from {pyre::memory}
    // storage strategies
    template <typename cellT>
    using heap_t = pyre::memory::heap_t<cellT>;
    template <typename cellT>
    using map_t = pyre::memory::constmap_t<cellT>;

    // aliases of hdf5 entities
    using dataset_t = H5::DataSet;
    using dataspace_t = H5::DataSpace;

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
