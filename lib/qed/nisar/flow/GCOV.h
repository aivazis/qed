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
// the local forward declarations
#include "forward.h"


// support
#include <pyre/flow.h>


// the reading of the mask of a GCOV product: the code {255} marks the cells outside the
// acquisition, painted faint brick red, the code {0} an invalid sample, painted black, and any
// other code names the subswath the sample came from; shown by itself, every subswath gets the
// color the GUNW mask gives the same subswath on both acquisitions
class qed::nisar::flow::GCOV {
    // type aliases
public:
    // me
    using self_type = GCOV;
    // the cells of a mask, wide enough for any of the codes on disk
    using mask_type = std::uint32_t;
    // the colors i paint
    using rgb_type = pyre::viz::rgb_t;
    // what a mask cell asks for: a color, or nothing for the color the pipeline chose
    using paint_type = std::optional<rgb_type>;
    // the color of every code the low byte of a mask can hold, when the mask is shown by itself
    using palette_type = std::array<rgb_type, 0x100>;
    // the spelling of types
    using string_type = pyre::flow::string_t;

    // interface
public:
    // the spelling of the template of the screens that read masks my way
    static inline auto screen() -> string_type;
    // the color of a cell with the given {mask}, if the mask has one to impose
    static inline auto paint(mask_type mask) -> paint_type;
    // the spelling of the template of the colormaps that show masks my way
    static inline auto colormap() -> string_type;
    // the colors of the codes, built the first time they are asked for
    static inline auto palette() -> const palette_type &;

    // metamethods
public:
    // the full set, declared explicitly
    GCOV() = default;
    GCOV(const GCOV &) = default;
    GCOV(GCOV &&) = default;
    GCOV & operator=(const GCOV &) = default;
    GCOV & operator=(GCOV &&) = default;
    ~GCOV() = default;
};

// get the inline definitions
#include "GCOV.icc"


// end of file
