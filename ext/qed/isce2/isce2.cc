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
qed::py::isce2::isce2(py::module & m)
{
    // create the {isce2} submodule
    auto isce2 = m.def_submodule(
        // the name of the module
        "isce2",
        // its docstring
        "support for isce2 readers and their infrastructure");

    // add support for the various products
    interferogram::interferogram(isce2);

    // all done
    return;
}


// end of file
