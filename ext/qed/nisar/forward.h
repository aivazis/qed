// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved

// code guard
#if !defined(qed_py_nisar_forward_h)
#define qed_py_nisar_forward_h


// set up the namespace
namespace qed::py::nisar {
    // the module linitializers
    // top level
    void nisar(py::module &);

    // data products
    void slc(py::module &);
    // profile
    void profile(py::module &);
    // stats
    void stats(py::module &);
}


#endif

// end of file
