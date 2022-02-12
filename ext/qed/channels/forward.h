// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_py_channels_forward_h)
#define qed_py_channels_forward_h


// the {channels} namespace
namespace qed::py::channels {
    // the subpackage intializaer
    void channels(py::module &);

    // the known channels
    void amplitude(py::module &);
    void complex(py::module &);
    void imaginary(py::module &);
    void phase(py::module &);
    void real(py::module &);
}


#endif

// end of file
