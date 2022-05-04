// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved

// code guard
#if !defined(qed_nisar_datatypes_complex_h)
#define qed_nisar_datatypes_complex_h


// the in-memory complex type that is compatible with the composite type in the NISAR data products
namespace qed::nisar::datatypes {
    template <typename valueT>
    inline auto complex() -> pyre::h5::comptype_t *;
}


// pull in the implementations
#define qed_nisar_datatypes_complex_icc
#include "complex.icc"
#undef qed_nisar_datatypes_complex_icc

#endif

// end of file
