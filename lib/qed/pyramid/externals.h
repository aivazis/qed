// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// stl
#include <cstdint>
#include <string>
// pyre
#include <pyre/journal.h>
#include <pyre/memory.h>
#include <pyre/grid.h>

// the pyramid storage
namespace qed::pyramid {
    // the name of a file
    using uri_t = std::string;
    // every raster qed serves is two dimensional, so the rank is fixed here once
    using index_t = pyre::grid::index_t<2>;
    using shape_t = pyre::grid::shape_t<2>;
    // a level is a box of cells diced into tiles, stored one tile after another; this is
    // the layout of its file, so a cell's offset in the file is a matter of arithmetic
    using packing_t = pyre::grid::chunked_t<2>;
    // the record of which tiles of a level were actually written: one byte per tile, in
    // tile order, and never a bit, so that two writers never share a byte
    using occupancy_t = pyre::memory::constmap_t<std::uint8_t>;
}    // namespace qed::pyramid

// end of file
