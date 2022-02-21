// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// the channels
#include "amplitude.h"
#include "complex.h"
#include "imaginary.h"
#include "phase.h"
#include "real.h"


// wrappers over {pyre::memory::map} template expansions
// build the submodule
void
qed::py::channels::channels(py::module & m)
{
    // create a {channels} submodule
    auto channels = m.def_submodule(
        // the name of the module
        "channels",
        // its docstring
        "support for predefined {channels}");

    // add the supported channels
    amplitude(channels);
    complex(channels);
    imaginary(channels);
    phase(channels);
    real(channels);

    // all done
    return;
}


// end of file
