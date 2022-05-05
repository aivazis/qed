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
qed::py::nisar::nisar(py::module & m)
{
    // create a {nisar} submodule
    auto nisar = m.def_submodule(
        // the name of the module
        "nisar",
        // its docstring
        "NISAR specific support");

    // add the supported nisar data types
    datatypes(nisar);
    // datasets
    slc(nisar);
    // profile
    profile(nisar);
    // stats
    stats(nisar);

    // all done
    return;
}


// end of file
