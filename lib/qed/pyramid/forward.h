// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// the pyramid storage
namespace qed::pyramid {
    // a decimated level of a raster, as a reader sees it
    template <class cellT>
    class Level;
    // a level under construction, as a builder writes it
    template <class cellT>
    class Draft;

    // the aliases clients use
    template <class cellT>
    using level_t = Level<cellT>;
    template <class cellT>
    using draft_t = Draft<cellT>;
}    // namespace qed::pyramid

// end of file
