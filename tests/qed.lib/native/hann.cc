// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
#include <cassert>
#include <cmath>
#include <complex>
// pyre
#include <pyre/journal.h>
#include <pyre/grid.h>
// the taper, pulled in through the native umbrella
#include <qed/native.h>


// type aliases
// a raster is a two dimensional canonically packed grid
using packing_t = pyre::grid::canonical_t<2>;
// of single precision complex cells held on the heap, like the ones read from an slc
using storage_t = pyre::memory::heap_t<std::complex<float>>;
// assembled into a grid
using grid_t = pyre::grid::grid_t<packing_t, storage_t>;
// its index
using index_t = grid_t::index_type;
// and its shape
using shape_t = grid_t::shape_type;


// make a raster of the given shape whose cells are all {value}
static auto
constant(int lines, int samples, std::complex<float> value) -> grid_t
{
    // make the grid
    auto grid = grid_t { packing_t(shape_t { lines, samples }), storage_t { lines * samples } };
    // go through its cells
    for (auto idx : grid.packing()) {
        // and set each one
        grid[idx] = value;
    }
    // hand it off
    return grid;
}


// check that the cell of {grid} at {line} and {sample} is {value}
static auto
check(const grid_t & grid, long line, long sample, std::complex<float> value) -> void
{
    // the cell
    auto cell = grid[index_t { line, sample }];
    // is the value, to single precision
    assert(std::abs(cell - value) < 1e-6);
    // all done
    return;
}


// exercise the taper
int
main(int argc, char * argv[])
{
    // initialize the journal
    pyre::journal::init(argc, argv);
    pyre::journal::application("qed");

    // the cells being tapered
    const auto one = std::complex<float>(2, -1);

    // five lines and four samples: the lines weigh {0, 1/2, 1, 1/2, 0}, the samples weigh
    // {0, 3/4, 3/4, 0}
    auto region = constant(5, 4, one);
    // taper it
    qed::native::hann(region);
    // the edges go to zero
    check(region, 0, 1, 0);
    check(region, 2, 0, 0);
    check(region, 4, 3, 0);
    // the middle line keeps the weight of the samples
    check(region, 2, 1, 0.75f * one);
    // and the other lines take a share of it
    check(region, 1, 2, 0.5f * 0.75f * one);
    check(region, 3, 1, 0.5f * 0.75f * one);

    // an axis one cell long has nowhere to taper to
    auto line = constant(1, 3, one);
    // so tapering a single line
    qed::native::hann(line);
    // only weighs its samples: {0, 1, 0}
    check(line, 0, 0, 0);
    check(line, 0, 1, one);
    check(line, 0, 2, 0);

    // all done
    return 0;
}


// end of file
