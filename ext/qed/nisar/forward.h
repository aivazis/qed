// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_py_nisar_forward_h)
#define qed_py_nisar_forward_h


// set up the namespace
namespace qed::py::nisar {
    // the module linitializers
    // top level
    void nisar(py::module &);

    // the submodule with the data type definitions
    void datatypes(py::module &);
    // the channel bindings
    void channels(py::module &);
}


#endif

// end of file
