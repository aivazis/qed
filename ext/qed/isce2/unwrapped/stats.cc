// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// stats
void
qed::py::isce2::unwrapped::stats(py::module & m)
{
    // the source arrives as a buffer; one wrapper rebuilds a read-only rank-3 grid over it and
    // dispatches on its cell type
    m.def(
        // the name of the function
        "stats",
        // the handler
        [](const py::buffer & source, std::vector<std::ptrdiff_t> origin,
           std::vector<std::ptrdiff_t> shape) -> stats_t {
            // rebuild the tile geometry as rank-3 grid coordinates
            auto o = asIndex<3>(origin);
            auto t = asShape<3>(shape);
            // dispatch on the buffer's cell type and collect the statistics of the matching grid
            return onGrid<3, float, double>(
                source, [&](const auto & grid) { return qed::isce2::unwrapped::stats(grid, o, t); });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a,
        // the docstring
        "compute the statistics of a tile");

    // all done
    return;
}


// end of file
