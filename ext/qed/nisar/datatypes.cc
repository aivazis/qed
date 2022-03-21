// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"

// the datatypes
#include "datatypes.h"


// amplitude
void
qed::py::nisar::datatypes(py::module & m)
{
    // create a submodule with definitions of NISAR specific datatypes
    auto datatypes = m.def_submodule(
        // the name of the module
        "datatypes",
        // its docstring
        "NISAR specific datatypes");


    // attach the complex type descriptions
    datatypes.attr("complexFloat") = complexType<float>();
    datatypes.attr("complexDouble") = complexType<double>();

    // all done
    return;
}


// end of file
