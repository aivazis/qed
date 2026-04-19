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
qed::py::nisar::mask(py::module & m)
{
    // create the {real} submodule
    auto mask = m.def_submodule(
        // the name of the module
        "mask",
        // its docstring
        "support for nisar {mask} datasets");

    // {unit8_t} bitmasks
    mask.def(
        // the name of the function
        "valid",
        // the handler
        &qed::nisar::mask::valid<heapgrid_t<uint8_t>>,
        // the signature
        "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a,
        // the docstring
        "render the value of a bitmask tile");

    // all done
    return;
}


// end of file
