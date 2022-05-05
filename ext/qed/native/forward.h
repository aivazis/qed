// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_py_forward_h)
#define qed_py_forward_h


// the {native} namespace
namespace qed::py::native {
    // the subpackage intializaer
    void native(py::module &);

    // the channel bindings
    void channels(py::module &);
    // profile
    void profile(py::module &);
    // statistics
    void stats(py::module &);
}


#endif

// end of file
