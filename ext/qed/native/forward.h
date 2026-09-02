// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once


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

// end of file
