// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// the BFPQ lookup table helper
#include "bfpq_lut.h"
// namespace setup
#include "forward.h"


// profile
void
qed::py::nisar::profile(py::module & m)
{
    // the nisar kernels read a path of samples out of an h5 dataset into a grid of a fixed cell
    // type, which the library converts the stored cells to; the result's cell type varies with the
    // dataset, so each wrapper hands it back as a python object

    // collect values along a path from a uint8 dataset
    m.def(
        // the name
        "profileUInt8",
        // the handler
        [](const dataset_t & source, const qed::native::points_t & points,
           bool closed) -> py::object {
            // read the path and hand it back
            return py::cast(qed::nisar::profile<heapgrid_t<std::uint8_t>>(source, points, closed));
        },
        // the signature
        "source"_a, "points"_a, "closed"_a = false,
        // the docstring
        "collect values from a uint8 dataset along a path");

    // collect values along a path from a float dataset
    m.def(
        // the name
        "profileFloat",
        // the handler
        [](const dataset_t & source, const qed::native::points_t & points,
           bool closed) -> py::object {
            // read the path and hand it back
            return py::cast(qed::nisar::profile<heapgrid_t<float>>(source, points, closed));
        },
        // the signature
        "source"_a, "points"_a, "closed"_a = false,
        // the docstring
        "collect values from a float dataset along a path");

    // collect values along a path from a complex float dataset
    m.def(
        // the name
        "profileComplexFloat",
        // the handler
        [](const dataset_t & source, const qed::native::points_t & points,
           bool closed) -> py::object {
            // read the path and hand it back
            return py::cast(
                qed::nisar::profile<heapgrid_t<std::complex<float>>>(source, points, closed));
        },
        // the signature
        "source"_a, "points"_a, "closed"_a = false,
        // the docstring
        "collect values from a complex float dataset along a path");

    // collect values along a path from a BFPQ encoded dataset
    m.def(
        // the name
        "profileBFPQ",
        // the handler
        [](const dataset_t & source, const py::buffer & lut, const qed::native::points_t & points,
           bool closed) -> py::object {
            // read and decode the path and hand it back
            return py::cast(
                qed::nisar::profileBFPQ<heapgrid_t<std::complex<float>>>(
                    source, asBFPQ(lut), points, closed));
        },
        // the signature
        "source"_a, "bfpq"_a, "points"_a, "closed"_a = false,
        // the docstring
        "collect values from a BFPQ encoded dataset along a path");

    // all done
    return;
}


// end of file
