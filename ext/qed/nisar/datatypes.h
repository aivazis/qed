// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_py_nisar_datatypes_h)
#define qed_py_nisar_datatypes_h


// implementations
template <typename valueT>
inline auto
qed::py::nisar::complexType() -> pyre::h5::comptype_t *
{
    // alias for my in-memory representation
    using complex_t = std::complex<valueT>;

    // make a new type
    auto complexTp = new pyre::h5::comptype_t(sizeof(complex_t));

    // add the real part
    complexTp->insertMember(
        // the name
        "r",
        // the offset
        0,
        // the type
        pyre::h5::datatype<typename complex_t::value_type>());

    // add the imaginary part
    complexTp->insertMember(
        // the name
        "i",
        // the offset
        sizeof(typename complex_t::value_type),
        // the type
        pyre::h5::datatype<typename complex_t::value_type>());

    // all done
    return complexTp;
}


#endif

// end of file
