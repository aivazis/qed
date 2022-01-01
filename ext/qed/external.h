// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_py_external_h)
#define qed_py_external_h


// STL
#include <memory>
#include <string>

// journal
#include <pyre/journal.h>

// pybind support
#include <pybind11/pybind11.h>
#include <pybind11/complex.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>


// type aliases
namespace qed::py {
    // import {pybind11}
    namespace py = pybind11;
    // get the special {pybind11} literals
    using namespace py::literals;

    // sizes of things
    using size_t = std::size_t;
    // strings
    using string_t = std::string;

    // pointer wrappers
    template <class T>
    using unique_pointer = std::unique_ptr<T>;
}


#endif

// end of file
