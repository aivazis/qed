// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// the bindings support, for {py::module}
#include "external.h"


// the {native} namespace
namespace qed::py::isce2::interferogram {
    // the subpackage intializaer
    void interferogram(py::module &);

    // the channel bindings
    void channels(py::module &);
    // profile
    void profile(py::module &);
    // statistics
    void stats(py::module &);
}

// end of file
