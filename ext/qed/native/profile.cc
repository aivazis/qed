// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// profile
void
qed::py::native::profile(py::module & m)
{
    // the source arrives as a buffer; one wrapper rebuilds a read-only rank-2 grid over it and
    // dispatches on its cell type, standing in for the old per-cell-type overload pile
    m.def(
        // the name of the function
        "profile",
        // the handler
        [](const py::buffer & source, const qed::native::points_t & points,
           bool closed) -> py::object {
            // dispatch on the buffer's cell type and collect values along the path; the result's
            // cell type varies, so hand it back as a python object rather than one fixed type
            return onGrid<2, char, int8_t, int16_t, int32_t, int64_t, float, double,
                          std::complex<float>, std::complex<double>>(
                source, [&](const auto & grid) -> py::object {
                    return py::cast(qed::native::profile(grid, points, closed));
                });
        },
        // the signature
        "source"_a, "points"_a, "closed"_a = false,
        // the docstring
        "collect values from a dataset along a path");

    // all done
    return;
}


// end of file
