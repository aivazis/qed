// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// code guard
#pragma once

// externals
#include <cmath>
#include <vector>
#include <tuple>

// declarations
namespace qed::api {

    // type aliases
    using pairs_t = std::vector<std::tuple<int, int>>;

    // the generator of shape guesses
    auto factor(long product, long aspect = 10) -> pairs_t;
}


// include the definitions
#include "api.icc"

// end of file
