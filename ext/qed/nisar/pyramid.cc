// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// pyramid
void
qed::py::nisar::pyramid(py::module & m)
{
    // the decimation reads a tile out of one h5 dataset into a grid of a fixed cell type
    // and writes it straight back out to another, so the data never crosses into python
    using grid_t = heapgrid_t<std::complex<float>>;

    // build a tile of a pyramid level from the level below it
    m.def(
        // the name
        "decimate",
        // the handler
        [](const dataset_t & source, const dataset_t & destination,
           const datatype_t & datatype, const py::iterable & origin,
           const py::iterable & shape, const py::iterable & stride) -> std::size_t {
            // read the strided tile and deposit it in the destination
            return qed::nisar::decimate<grid_t>(
                source, destination, datatype, asIndex<2>(origin), asShape<2>(shape),
                asIndex<2>(stride));
        },
        // the signature
        "source"_a, "destination"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a,
        // the docstring
        "fill the {destination} tile at {origin}+{shape} by decimating {source} by "
        "{stride}, and report how many of its cells were not fill");

    // all done
    return;
}


// end of file
