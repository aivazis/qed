// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// build the submodule
void
qed::py::isce2::unwrapped::unwrapped(py::module & m)
{
    // create the {native} submodule
    auto unwrapped = m.def_submodule(
        // the name of the module
        "unwrapped",
        // its docstring
        "support for isce2 unwrapped readers and their infrastructure");

    // add the channel bindings
    channels(unwrapped);
    // profile
    profile(unwrapped);
    // statistics
    stats(unwrapped);

    // all done
    return;
}


// end of file
