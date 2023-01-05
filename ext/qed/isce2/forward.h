// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved

// code guard
#if !defined(qed_py_isce2_forward_h)
#define qed_py_isce2_forward_h


// the {isce2} namespace
namespace qed::py::isce2 {
    // the subpackage initializer
    void isce2(py::module &);

    // the various products
    namespace interferogram {
        void interferogram(py::module &);
    }
    namespace unwrapped {
        void unwrapped(py::module &);
    }
}


#endif

// end of file
