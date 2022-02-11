// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


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


// amplitude
void
qed::py::channels::amplitude(py::module & m)
{
    // all done
    return;
}


// complex
void
qed::py::channels::complex(py::module & m)
{
    // all done
    return;
}


// imaginary
void
qed::py::channels::imaginary(py::module & m)
{
    // all done
    return;
}


// phase
void
qed::py::channels::phase(py::module & m)
{
    // all done
    return;
}


// real
void
qed::py::channels::real(py::module & m)
{
    // all done
    return;
}


// end of file
