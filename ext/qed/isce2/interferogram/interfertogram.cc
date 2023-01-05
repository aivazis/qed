// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// build the submodule
void
qed::py::isce2::interferogram::interferogram(py::module & m)
{
    // create the {native} submodule
    auto interferogram = m.def_submodule(
        // the name of the module
        "interferogram",
        // its docstring
        "support for isce2 interferogram readers and their infrastructure");

    // add the channel bindings
    channels(interferogram);
    // profile
    profile(interferogram);
    // statistics
    stats(interferogram);

    // all done
    return;
}


// end of file
