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
}


#endif

// end of file
