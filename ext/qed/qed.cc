// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// the module entry point
PYBIND11_MODULE(qed, m)
{
    // the doc string
    m.doc() = "the libqed bindings";

    // bind the opaque types
    qed::py::opaque(m);
    // register the exception types
    qed::py::exceptions(m);

    // version info
    qed::py::version(m);
}


// end of file
