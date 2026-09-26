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
        [](const py::buffer & source, const py::iterable & origin,
           const py::iterable & shape) -> stats_t {
            // rebuild the tile geometry as rank-3 grid coordinates
            auto o = asIndex<3>(origin);
            auto t = asShape<3>(shape);
            // dispatch on the buffer's cell type and collect the statistics of the matching grid
            return onGrid<3, float, double>(source, [&](const auto & grid) {
                return qed::isce2::unwrapped::stats(grid, o, t);
            });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a,
        // the docstring
        "compute the statistics of a tile");

    // collect a mergeable sample of one band of a strided tile, the render footprint of a
    // decimated view
    m.def(
        // the name of the function
        "sample",
        // the handler
        [](const py::buffer & source, long band, const py::iterable & origin,
           const py::iterable & shape, const py::iterable & stride) -> sample_t {
            // the tile geometry arrives in the coordinates of the raster, as (line, sample)
            auto o = asIndex<2>(origin);
            auto t = asShape<2>(shape);
            auto s = asIndex<2>(stride);
            // lift it into the line interleaved layout, one band thick
            auto o3 = pyre::grid::index_t<3> { o[0], band, o[1] };
            auto t3 = pyre::grid::shape_t<3> { t[0], 1, t[1] };
            auto s3 = pyre::grid::index_t<3> { s[0], 1, s[1] };
            // dispatch on the buffer's cell type and sample the band
            return onGrid<3, float, double>(source, [&](const auto & grid) {
                return qed::isce2::unwrapped::sample(grid, band, o3, t3, s3);
            });
        },
        // the signature
        "source"_a, "band"_a, "origin"_a, "shape"_a, "stride"_a,
        // the docstring
        "collect a mergeable statistical sample of {band} of the strided tile at "
        "{origin}+{shape}");

    // all done
    return;
}


// end of file
