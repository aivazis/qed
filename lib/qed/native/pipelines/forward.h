// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// external dependencies and the local type aliases
#include "../externals.h"
// the namespace and its forward declarations
#include "../forward.h"


// the visualization pipelines that are assembled out of the factories of {pyre::flow}
namespace qed::native::pipelines {
    // the value of a real tile, painted gray
    class Value;
    // the amplitude of a complex tile, painted gray
    template <typename cellT>
    class Amplitude;
} // namespace qed::native::pipelines


// end of file
