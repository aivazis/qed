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


// type aliases
namespace qed::py::channels {
    // from {pyre::memory}
    // storage strategies
    template <typename cellT>
    using map_t = pyre::memory::constmap_t<cellT>;

    // from {pyre::grid}
    // layouts
    using layout_t = pyre::grid::canonical_t<2>;
    // grids
    template <typename cellT>
    using source_t = pyre::grid::grid_t<layout_t, map_t<cellT>>;

    // from {pyre::viz}
    // encodings
    using bmp_t = pyre::viz::bmp_t;

    // color maps
    template <typename sourceT>
    using gray_t = pyre::viz::colormaps::gray_t<sourceT>;

    // filters
    // computing the amplitude of a complex source
    template <typename sourceT>
    using amplitude_t = pyre::viz::filters::amplitude_t<sourceT>;
    // support for zooming
    template <typename sourceT>
    using decimate_t = pyre::viz::filters::decimate_t<sourceT>;
    // mapping a range of values to the unit interval
    template <typename sourceT>
    using parametric_t = pyre::viz::filters::parametric_t<sourceT>;
}


#endif

// end of file
