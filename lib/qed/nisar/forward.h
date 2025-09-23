// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved

// code guard
#pragma once

namespace qed::nisar {
    // the BFPQ lookup table
    using bfqp_lut_storage_t = pyre::memory::heap_t<float>;
    using bfpq_lut_layout_t = pyre::grid::canonical_t<1>;
    using bfpq_lut_t = pyre::grid::grid_t<bfpq_lut_layout_t, bfqp_lut_storage_t>;

    // storage for a BFPQ encoded tile
    using bfpq_slc_cell_t = std::complex<std::uint16_t>;
    using bfpq_slc_storage_t = pyre::memory::heap_t<bfpq_slc_cell_t>;
    using bfpq_slc_layout_t = pyre::grid::canonical_t<2>;
    using bfpq_slc_t = pyre::grid::grid_t<bfpq_slc_layout_t, bfpq_slc_storage_t>;
}


// end of file
