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
qed::py::isce2::interferogram::stats(py::module & m)
{
    // the source arrives as a buffer; one wrapper rebuilds a read-only rank-2 grid over it and
    // dispatches on its cell type
    m.def(
        // the name of the function
        "stats",
        // the handler
        [](const py::buffer & source, const py::iterable & origin,
           const py::iterable & shape) -> stats_t {
            // rebuild the tile geometry as rank-2 grid coordinates
            auto o = asIndex<2>(origin);
            auto t = asShape<2>(shape);
            // dispatch on the buffer's cell type and collect the statistics of the matching grid
            return onGrid<2, std::complex<float>, std::complex<double>>(
                source, [&](const auto & grid) { return qed::native::stats(grid, o, t); });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a,
        // the docstring
        "compute the statistics of a tile");

    // all done
    return;
}


// end of file
