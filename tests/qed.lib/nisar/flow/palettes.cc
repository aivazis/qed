// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
#include <cassert>
#include <cstdint>
// pyre
#include <pyre/journal.h>
#include <pyre/grid.h>
#include <pyre/viz.h>
// the flow nodes and the mask kernels, pulled in through the nisar umbrella
#include <qed/nisar.h>


// type aliases
// the mask kernels read their codes into a two dimensional grid of bytes
using packing_t = pyre::grid::canonical_t<2>;
// on the heap
using storage_t = pyre::memory::heap_t<std::uint8_t>;
// assembled into a grid
using grid_t = pyre::grid::grid_t<packing_t, storage_t>;


// check that the colormaps of the flow show every code of a mask in exactly the color the mask
// kernel of the same product draws it, for each of the 256 codes the low byte can hold
int
main(int argc, char * argv[])
{
    // initialize the journal
    pyre::journal::init(argc, argv);
    pyre::journal::application("qed");

    // a one cell grid for the kernels to hold on to; they only read it when they are advanced
    packing_t packing { grid_t::shape_type { 1, 1 } };
    // its storage
    storage_t store { packing.cells() };
    // and the grid
    grid_t codes { packing, store };

    // the mask kernels, which build their palettes when they are made
    auto gunw = qed::nisar::masks::GUNWMask<grid_t>(codes);
    auto gcov = qed::nisar::masks::GCOVMask<grid_t>(codes);
    // and the palettes of the flow
    const auto & gunwPalette = qed::nisar::flow::GUNW::palette();
    const auto & gcovPalette = qed::nisar::flow::GCOV::palette();

    // go through every code
    for (int code = 0; code < 0x100; ++code) {
        // the color of the GUNW kernel
        const auto gunwColor = gunw.palette(code);
        // must be the color of the GUNW colormap, exactly
        assert(gunwColor == gunwPalette[code]);
        // the color of the GCOV kernel
        const auto gcovColor = gcov.palette(code);
        // must be the color of the GCOV colormap, exactly
        assert(gcovColor == gcovPalette[code]);
    }

    // all done
    return 0;
}


// end of file
