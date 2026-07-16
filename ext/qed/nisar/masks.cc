// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for mask visualization pipelines
void
qed::py::nisar::masks(py::module & m)
{
    // create the {masks} submodule
    auto masks = m.def_submodule(
        // the name of the module
        "masks",
        // its docstring
        "support for nisar {mask} datasets");

    // {uint8_t} GUNW bitmasks
    masks.def(
        // the name of the function
        "gunw",
        // the handler
        &qed::nisar::masks::gunw<heapgrid_t<uint8_t>>,
        // the signature
        "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a,
        // the docstring
        "render a tile of a GUNW product mask");

    // {uint8_t} GCOV bitmasks
    masks.def(
        // the name of the function
        "gcov",
        // the handler
        &qed::nisar::masks::gcov<heapgrid_t<uint8_t>>,
        // the signature
        "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a,
        // the docstring
        "render a tile of a GCOV product mask");

    // all done
    return;
}


// end of file
