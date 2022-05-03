// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// build the submodule
void
qed::py::native::native(py::module & m)
{
    // create the {native} submodule
    auto native = m.def_submodule(
        // the name of the module
        "native",
        // its docstring
        "support for native readers and their infrastructure");

    // add the channel bindings
    channels(native);

    // all done
    return;
}


// end of file
