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
        // the initializer
        void channels(py::module &);
    }
    // datasets subpackage
    namespace datasets {
        // the initializer
        void datasets(py::module &);
    }

    // nisar support
    namespace nisar {
        // the initializer
        void nisar(py::module &);
    }
}


#endif

// end of file
