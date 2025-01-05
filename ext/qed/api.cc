// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
#include "external.h"
// namespace setup
#include "forward.h"

// the qed library
#include <qed/api.h>


// access to the version tags of the library and the bindings
void
qed::py::api(py::module & m)
{
    // generator of guesses of raster shapes
    m.def(
        // the name
        "factor",
        // the implementation
        &qed::api::factor,
        // the signature
        "product"_a, "aspect"_a,
        // the docstring
        "generate pairs of numbers with a given {product} whose {aspect} ratio does not exceed "
        "a given value");


    // all done
    return;
}


// end of file
