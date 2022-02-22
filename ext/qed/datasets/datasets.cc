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
qed::py::datasets::datasets(py::module & m)
{
    // create the {datasets} submodule
    auto datasets = m.def_submodule(
        // the name of the module
        "datasets",
        // its docstring
        "support for dataset specific operations");

    // add the interface
    stats(datasets);

    // all done
    return;
}


// end of file
