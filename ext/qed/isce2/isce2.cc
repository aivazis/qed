// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// wrappers over {pyre::memory::map} template expansions
// build the submodule
void
qed::py::isce2::isce2(py::module & m)
{
    // create a {memory} submodule
    auto memory = m.def_submodule(
        // the name of the module
        "isce2",
        // its docstring
        "support for {isce2} specific entities");

    // all done
    return;
}


// end of file
