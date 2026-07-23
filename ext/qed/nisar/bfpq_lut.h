// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once


// the nisar aliases and the grid dispatch helpers
#include "external.h"
// for copying the lookup table entries
#include <algorithm>


namespace qed::py {
    // rebuild the BFPQ lookup table grid from a python buffer: the reader hands us the LUT as a
    // buffer (the decoded contents of the {BFPQLUT} dataset), and the kernels want it as a small
    // one-dimensional heap grid of floats, so copy the entries into a fresh block
    inline auto asBFPQ(const py::buffer & lut) -> qed::nisar::bfpq_lut_t
    {
        // read the buffer description
        auto info = lut.request();
        // the number of entries
        auto cells = static_cast<std::ptrdiff_t>(info.size);
        // a one-dimensional layout over them
        auto layout = pyre::grid::canonical_t<1>(pyre::grid::shape_t<1> { cells });
        // a fresh heap block sized to hold them
        auto storage = pyre::memory::heap_t<float> { cells };
        // copy the lookup table entries in; they are single precision floats
        auto source = static_cast<const float *>(info.ptr);
        std::copy(source, source + cells, storage.data());
        // pair the layout and storage into the lookup table grid
        return qed::nisar::bfpq_lut_t(layout, storage);
    }
} // namespace qed::py


// end of file
