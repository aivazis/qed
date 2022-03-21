// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_py_nisar_forward_h)
#define qed_py_nisar_forward_h


// set up the namespace
namespace qed::py::nisar {
    // the module linitializers
    // top level
    void nisar(py::module &);
    // the submodule with the data type definitions
    void datatypes(py::module &);


    // in-memory layout for the composite type that encodes complex values in NISAR products
    // we use {pyre::grid} of {std::complex<float>}, and need the names of the members
    // of the in-file composite type in order to make the mapping work
    template <typename valueT>
    inline auto complexType() -> pyre::h5::comptype_t *;
}


#endif

// end of file
