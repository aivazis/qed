// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// the bindings support, for {py::module}
#include "external.h"


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

// end of file
