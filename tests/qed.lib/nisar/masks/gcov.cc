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
#include <vector>
// pyre
#include <pyre/journal.h>
#include <pyre/grid.h>
#include <pyre/viz.h>
// the renderers under test, pulled in through the nisar umbrella
#include <qed/nisar.h>


// type aliases
// a mask tile is a two dimensional canonically packed grid
using packing_t = pyre::grid::canonical_t<2>;
// of unsigned bytes held on the heap, matching the {uint8_t} bitmask binding
using storage_t = pyre::memory::heap_t<std::uint8_t>;
// assembled into a grid
using grid_t = pyre::grid::grid_t<packing_t, storage_t>;
// the real GCOV mask renderer, instantiated over our grid so we exercise the shipping palette
using gcovmask_t = qed::nisar::masks::GCOVMask<grid_t>;
// and the GUNW renderer, so we can prove the two palettes agree on the subswath colors
using gunwmask_t = qed::nisar::masks::GUNWMask<grid_t>;
// the bmp codec that turns the color stream into a file image
using bmp_t = pyre::viz::iterators::codecs::bmp_t;


// assemble the ordered list of GCOV mask codes we want to display
// per the product spec: {0} marks invalid/partially-focused samples, {1..5} name the subswath of
// a valid sample, and {255} fills pixels outside the radar acquisition extent
static auto
maskCodes() -> std::vector<int>
{
    // start an empty list
    auto codes = std::vector<int> {};
    // lead with the invalid-sample code, which the palette leaves black
    codes.push_back(0);
    // the subswath codes, one per subswath
    for (int d = 1; d <= 5; ++d) {
        // record the subswath code
        codes.push_back(d);
    }
    // and finally the fill value
    codes.push_back(255);
    // hand back the list
    return codes;
}


// build a synthetic GCOV mask and render it to a bmp so the palette can be inspected by eye
int
main(int argc, char * argv[])
{
    // initialize the journal
    pyre::journal::init(argc, argv);
    pyre::journal::application("qed");

    // the tile is a fixed width
    const int width = 1024;
    // each mask code gets a strip this many rows tall
    const int stripHeight = 128;

    // collect the codes we want to display
    const auto codes = maskCodes();
    // one horizontal strip per code
    const auto strips = static_cast<int>(codes.size());
    // the tile is exactly tall enough to hold one strip per code
    const int height = strips * stripHeight;

    // lay out the grid
    packing_t packing { grid_t::shape_type { height, width } };
    // allocate its storage
    storage_t store { packing.cells() };
    // and assemble the grid
    grid_t mask { packing, store };

    // fill the grid with horizontal strips
    for (auto idx : mask.layout()) {
        // the row index selects the strip; each strip is exactly {stripHeight} rows tall
        const int strip = static_cast<int>(idx[0]) / stripHeight;
        // stamp this pixel with the strip's mask code
        mask[idx] = static_cast<std::uint8_t>(codes[strip]);
    }

    // build the real GCOV renderer over the synthetic mask
    auto renderer = gcovmask_t(mask);
    // and a GUNW renderer so we can compare palettes; the source data is irrelevant to the palette
    auto reference = gunwmask_t(mask);

    // guard the spec: each subswath {d} must render with the color the GUNW mask assigns to its
    // diagonal code {11*d}, i.e. reference subswath == secondary subswath == {d}
    for (int d = 1; d <= 5; ++d) {
        // the GCOV color for this subswath
        const auto got = renderer.palette(d);
        // the GUNW diagonal color for the same subswath
        const auto want = reference.palette(11 * d);
        // they must be identical, channel for channel
        assert(got.red == want.red && got.green == want.green && got.blue == want.blue);
    }

    // guard the fix: the fill code 255 must resolve to its assigned color, not out-of-bounds garbage
    const auto fill = renderer.palette(255);
    // the shipping fill color is a dark red-brown; check each channel with a float tolerance
    assert(std::abs(fill.red - 0.150f) < 1e-6f);
    assert(std::abs(fill.green - 0.050f) < 1e-6f);
    assert(std::abs(fill.blue - 0.050f) < 1e-6f);

    // make a bitmap of the right size
    auto bmp = bmp_t(height, width);
    // encode the color stream into it
    bmp.encode(renderer);

    // open the output file beside this generator
    auto stream = std::ofstream("gcov.bmp", std::ios::out | std::ios::binary);
    // if it opened
    if (stream.is_open()) {
        // write the whole bmp payload
        stream.write(reinterpret_cast<const char *>(bmp.data()), bmp.bytes());
    }

    // all done
    return 0;
}


// end of file
