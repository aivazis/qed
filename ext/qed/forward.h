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

    // channels subpackage
    namespace channels {
        // the initializer; everything else is private to the subpackage
        void channels(py::module &);
    }
    // datasets subpackage
    namespace datasets {
        // the initializer; everything else is private to the subpackage
        void datasets(py::module &);
    }
}


#endif

// end of file
