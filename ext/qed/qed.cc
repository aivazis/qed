// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


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

    // support for readers, their datasets and visualization pipelines
    qed::py::native::native(m);
    qed::py::isce2::isce2(m);
    qed::py::nisar::nisar(m);
}


// end of file
