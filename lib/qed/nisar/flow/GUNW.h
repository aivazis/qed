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


// the reading of the mask of a GUNW product: the low byte holds a three digit code whose last two
// digits name the subswaths of the reference and the secondary acquisitions, so a cell where
// either one is zero was not covered by both, and is painted black over a measurement; shown by
// itself, every code gets the color of its subswaths, land or water
class qed::nisar::flow::GUNW {
    // type aliases
public:
    // me
    using self_type = GUNW;
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
    GUNW() = default;
    GUNW(const GUNW &) = default;
    GUNW(GUNW &&) = default;
    GUNW & operator=(const GUNW &) = default;
    GUNW & operator=(GUNW &&) = default;
    ~GUNW() = default;
};

// get the inline definitions
#include "GUNW.icc"


// end of file
