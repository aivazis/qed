// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// the bindings support, for {py::module}
#include "external.h"


// useful type aliases
namespace qed::py {
}

// the {qed} namespace
namespace qed::py {
    // bindings of opaque types
    void opaque(py::module &);
    // exceptions
    void exceptions(py::module &);

    // top level function
    void api(py::module &);
    // version info
    void version(py::module &);

    // datasets subpackage
    namespace datasets {
        // the initializer
        void datasets(py::module &);
    }

    // native support
    namespace native {
        // the initializer
        void native(py::module &);
    }
    // isce2 support
    namespace isce2 {
        // the initializer
        void isce2(py::module &);
    }
    // nisar support
    namespace pyramid {
        void pyramid(py::module &);
    }
    namespace nisar {
        // the initializer
        void nisar(py::module &);
    }
}

// end of file
