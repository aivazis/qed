// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_py_forward_h)
#define qed_py_forward_h


// useful type aliases
namespace qed::py {
}

// the {qed} namespace
namespace qed::py {
    // bindings of opaque types
    void opaque(py::module &);
    // exceptions
    void exceptions(py::module &);

    // version info
    void version(py::module &);

    // isce2 subpackage
    namespace isce2 {
        // the initializer; everything else is private to the subpackage
        void isce2(py::module &);
    }
}


#endif

// end of file
