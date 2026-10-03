// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
#include <cassert>
#include <cmath>
#include <complex>
#include <numbers>
// pyre
#include <pyre/journal.h>
#include <pyre/grid.h>
#include <pyre/viz.h>
// the transform and its renderer, pulled in through the native umbrella
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


// the shape of the rasters; uneven sides, so a mix up of the two axes shows
constexpr int lines = 8;
constexpr int samples = 6;
// the number of their cells
constexpr int cells = lines * samples;
// the size of a pixel in the rendered tile, in bytes
constexpr int pixel = 3;
// where the pixels start in the rendered tile
constexpr int payload = 54;
// the length of a line of pixels, padded to a multiple of four bytes
constexpr int stride = ((samples * pixel + 3) / 4) * 4;


// make a raster whose cells are the plane wave with the given frequency along each axis
static auto
wave(int k0, int k1) -> grid_t
{
    // make the grid
    auto grid = grid_t { packing_t(shape_t { lines, samples }), storage_t { cells } };
    // go through its cells
    for (auto idx : grid.packing()) {
        // the phase of the wave at this cell
        auto phase = 2 * std::numbers::pi
                   * (static_cast<double>(k0 * idx[0]) / lines
                      + static_cast<double>(k1 * idx[1]) / samples);
        // set the cell
        grid[idx] = std::complex<float>(std::cos(phase), std::sin(phase));
    }
    // hand it off
    return grid;
}


// check that the only frequency in {spectrum} with any amplitude is the one at {peak}
static auto
single(const grid_t & spectrum, index_t peak) -> void
{
    // go through the frequencies
    for (auto idx : spectrum.packing()) {
        // the amplitude of this one
        auto amplitude = std::abs(spectrum[idx]);
        // the peak carries all the energy of a wave of unit amplitude
        if (idx == peak) {
            // so it is the number of cells
            assert(std::abs(amplitude - cells) < 1e-3);
        }
        // and every other frequency
        else {
            // has none
            assert(amplitude < 1e-3);
        }
    }
    // all done
    return;
}


// the gray level of the pixel of {bmp} at {line} and {sample}
static auto
gray(const qed::native::bmp_t & bmp, int line, int sample) -> int
{
    // the pixels of the tile
    auto data = reinterpret_cast<const unsigned char *>(bmp.data());
    // the first byte of the pixel
    auto spot = payload + line * stride + sample * pixel;
    // a gray pixel has the same value in all three of its channels
    assert(data[spot] == data[spot + 1] && data[spot] == data[spot + 2]);
    // which is its gray level
    return data[spot];
}


// exercise the transform and the rendering of its spectrum
int
main(int argc, char * argv[])
{
    // initialize the journal
    pyre::journal::init(argc, argv);
    pyre::journal::application("qed");

    // a constant raster
    auto constant = wave(0, 0);
    // has all of its energy at zero frequency
    auto flat = qed::native::fft(constant);
    single(flat, index_t { 0, 0 });
    // and the transform leaves its source alone
    assert(std::abs(constant[index_t { 3, 2 }] - std::complex<float>(1, 0)) < 1e-6);

    // a wave with a frequency along each axis
    auto tilted = qed::native::fft(wave(2, 1));
    // has all of its energy at that frequency
    single(tilted, index_t { 2, 1 });

    // render the spectrum of the constant raster over sixty decibels
    auto tile = qed::native::channels::spectrum(flat, 60);
    // the tile has a pixel for every frequency, and its header
    assert(tile.bytes() == payload + lines * stride);
    // zero frequency moved to the center, where it is as bright as it gets
    assert(gray(tile, lines / 2, samples / 2) == 255);
    // and the frequencies with no power are black
    assert(gray(tile, 0, 0) == 0);
    assert(gray(tile, lines - 1, samples - 1) == 0);

    // all done
    return 0;
}


// end of file
