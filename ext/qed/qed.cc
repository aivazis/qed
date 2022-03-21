// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


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

    // plugins
    qed::py::channels::channels(m);
    qed::py::datasets::datasets(m);

    // NISAR support
    qed::py::nisar::nisar(m);
}


// end of file
