// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
#include <cassert>
#include <cmath>
#include <cstdint>
#include <fstream>
// pyre
#include <pyre/journal.h>
#include <pyre/grid.h>
#include <pyre/viz.h>
// the renderer under test, pulled in through the nisar umbrella
#include <qed/nisar.h>


// type aliases
// a mask tile is a two dimensional canonically packed grid
using packing_t = pyre::grid::canonical_t<2>;
// of unsigned bytes held on the heap, matching the {uint8_t} bitmask binding
using storage_t = pyre::memory::heap_t<std::uint8_t>;
// assembled into a grid
using grid_t = pyre::grid::grid_t<packing_t, storage_t>;
// the real GUNW mask renderer, instantiated over our grid so we exercise the shipping palette
using gunwmask_t = qed::nisar::masks::GUNWMask<grid_t>;
// the bmp codec that turns the color stream into a file image
using bmp_t = pyre::viz::iterators::codecs::bmp_t;


// build a synthetic GUNW mask and render it to a bmp so the palette can be inspected by eye
// the GUNW mask code is a three-digit number {water*100 + ref*10 + sec}: the reference and
// secondary RSLC subswaths in {1..5}, with a 0 in either digit marking an invalid sample, and
// the hundreds digit flagging water in the reference RSLC
int
main(int argc, char * argv[])
{
    // initialize the journal
    pyre::journal::init(argc, argv);
    pyre::journal::application("qed");

    // the tile is a fixed width
    const int width = 1024;
    // each row of the layout is a strip this many pixels tall
    const int stripHeight = 128;
    // the subswath axes both run over five values
    const int subswaths = 5;

    // the vertical layout, top to bottom: one invalid strip, a five-row land block, a five-row
    // water block, and one fill strip
    const int strips = 1 + subswaths + subswaths + 1;
    // so the tile is exactly tall enough to hold them
    const int height = strips * stripHeight;

    // lay out the grid
    packing_t packing { grid_t::shape_type { height, width } };
    // allocate its storage
    storage_t store { packing.cells() };
    // and assemble the grid
    grid_t mask { packing, store };

    // fill the grid
    for (auto idx : mask.layout()) {
        // the strip this pixel falls in, from top to bottom
        const int strip = static_cast<int>(idx[0]) / stripHeight;
        // the secondary subswath is selected by the column, evenly split into five bands
        const int sec = 1 + static_cast<int>(idx[1]) * subswaths / width;

        // the mask code we will stamp here
        int code = 0;
        // the first strip shows the invalid value
        if (strip == 0) {
            // the canonical invalid sample: a zero in both subswath digits
            code = 0;
        }
        // the next five strips are the land block: reference subswath {1..5} down the rows
        else if (strip <= subswaths) {
            // the reference subswath is the strip index within the block
            const int ref = strip;
            // land code: no water, the two subswath digits
            code = 10 * ref + sec;
        }
        // the following five strips repeat the block with the water flag turned on
        else if (strip <= 2 * subswaths) {
            // the reference subswath is the strip index within this second block
            const int ref = strip - subswaths;
            // water code: the same subswath pair, lifted into the water range
            code = 100 + 10 * ref + sec;
        }
        // the last strip shows the fill value
        else {
            // pixels outside the acquisition extent
            code = 255;
        }

        // stamp the pixel
        mask[idx] = static_cast<std::uint8_t>(code);
    }

    // build the real renderer over the synthetic mask
    auto renderer = gunwmask_t(mask);

    // guard the fix: the fill code 255 must resolve to its assigned color, not out-of-bounds garbage
    const auto fill = renderer.palette(255);
    // the shipping fill color is a dark red-brown; check each channel with a float tolerance
    assert(std::abs(fill.red - 0.150f) < 1e-6f);
    assert(std::abs(fill.green - 0.050f) < 1e-6f);
    assert(std::abs(fill.blue - 0.050f) < 1e-6f);

    // guard the invalid class: a zero subswath digit renders black
    const auto invalid = renderer.palette(0);
    // all three channels are off
    assert(invalid.red == 0.f && invalid.green == 0.f && invalid.blue == 0.f);

    // guard the water flag: land and water share the subswath pair but must not share a color
    for (int ref = 1; ref <= subswaths; ++ref) {
        // walk the secondary subswath
        for (int sec = 1; sec <= subswaths; ++sec) {
            // the land color for this pair
            const auto land = renderer.palette(10 * ref + sec);
            // the water color for the same pair
            const auto water = renderer.palette(100 + 10 * ref + sec);
            // they must differ in at least one channel
            assert(land.red != water.red || land.green != water.green || land.blue != water.blue);
        }
    }

    // make a bitmap of the right size
    auto bmp = bmp_t(height, width);
    // encode the color stream into it
    bmp.encode(renderer);

    // open the output file beside this generator
    auto stream = std::ofstream("gunw.bmp", std::ios::out | std::ios::binary);
    // if it opened
    if (stream.is_open()) {
        // write the whole bmp payload
        stream.write(reinterpret_cast<const char *>(bmp.data()), bmp.bytes());
    }

    // all done
    return 0;
}


// end of file
