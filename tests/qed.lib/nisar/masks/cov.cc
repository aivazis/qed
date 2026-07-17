// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
#include <cassert>
#include <cmath>
#include <cstdint>
#include <vector>
// pyre
#include <pyre/journal.h>
#include <pyre/grid.h>
#include <pyre/viz.h>
// the workflow under test, pulled in through the nisar umbrella
#include <qed/nisar.h>


// type aliases
// both tiles are two dimensional canonically packed grids
using packing_t = pyre::grid::canonical_t<2>;
// the covariance source holds single precision samples on the heap
using source_storage_t = pyre::memory::heap_t<float>;
// assembled into a grid
using source_t = pyre::grid::grid_t<packing_t, source_storage_t>;
// the mask is read into a {uint32} buffer, matching the covarianceMasked pipeline
using mask_storage_t = pyre::memory::heap_t<std::uint32_t>;
// assembled into a grid
using mask_t = pyre::grid::grid_t<packing_t, mask_storage_t>;
// the masked covariance workflow instantiated over the two grids, so we exercise the shipping gate
using workflow_t = qed::nisar::real::MaskedCovariance<source_t, mask_t>;


// the ordered mask codes we want to probe
// per the GCOV spec: {0} marks an invalid/partially-focused sample, a non-zero code names the
// subswath the sample came from, and {255} fills pixels outside the radar acquisition extent
static auto
maskCodes() -> std::vector<std::uint32_t>
{
    // start an empty list
    auto codes = std::vector<std::uint32_t> {};
    // lead with the invalid-sample code, which the gate must paint black
    codes.push_back(0);
    // the five subswath codes, all of which must show the covariance color
    for (std::uint32_t d = 1; d <= 5; ++d) {
        // record the subswath code
        codes.push_back(d);
    }
    // a couple of larger non-zero codes, to prove any non-fill subswath renders the color
    codes.push_back(100);
    codes.push_back(254);
    // and finally the fill value, which must render the faint red
    codes.push_back(255);
    // hand back the list
    return codes;
}


// verify that the masked covariance gate honors the GCOV mask convention: {0} is invalid and
// renders black, {255} is fill and renders a faint red, and every other code names a valid
// subswath and shows the covariance color
int
main(int argc, char * argv[])
{
    // initialize the journal
    pyre::journal::init(argc, argv);
    pyre::journal::application("qed");

    // collect the codes we want to probe
    const auto codes = maskCodes();
    // one sample per code, laid out in a single row
    const int width = static_cast<int>(codes.size());

    // lay out the shared {1 x width} tile
    packing_t packing { source_t::shape_type { 1, width } };

    // allocate the covariance source storage
    source_storage_t sourceStore { packing.cells() };
    // and assemble the source grid
    source_t source { packing, sourceStore };
    // fill it with a constant mid-range value so a valid sample never normalizes to black
    for (auto idx : source.layout()) {
        // stamp the midpoint of our {0, 1} brightness interval
        source[idx] = 0.5f;
    }

    // allocate the mask storage
    mask_storage_t maskStore { packing.cells() };
    // and assemble the mask grid
    mask_t mask { packing, maskStore };
    // stamp each column with its probe code
    for (auto idx : mask.layout()) {
        // the column index selects the code
        mask[idx] = codes[idx[1]];
    }

    // build the workflow over the two tiles, normalizing against a {0, 1} brightness interval
    auto workflow = workflow_t(source, mask, 0.0, 1.0);

    // walk the row, one column per mask code
    for (int col = 0; col < width; ++col) {
        // the code under the cursor
        const auto code = codes[col];
        // the color the gate produces for it
        const auto color = *workflow;
        // the invalid code must be painted pure black
        if (code == 0) {
            // all three channels vanish
            assert(color.red == 0.0 && color.green == 0.0 && color.blue == 0.0);
        }
        // the fill code must render the faint red, channel for channel within a float tolerance
        else if (code == 255) {
            // the shipping fill color is a dark red-brown
            assert(std::abs(color.red - 0.10) < 1e-6);
            assert(std::abs(color.green - 0.05) < 1e-6);
            assert(std::abs(color.blue - 0.05) < 1e-6);
        }
        // every other code names a valid subswath and shows the covariance color
        else {
            // the constant mid-range sample renders as an equal-channel gray at the midpoint
            assert(color.red == color.green && color.green == color.blue);
            // which is emphatically not black
            assert(std::abs(color.red - 0.5) < 1e-6);
        }
        // advance to the next column
        ++workflow;
    }

    // all done
    return 0;
}


// end of file
