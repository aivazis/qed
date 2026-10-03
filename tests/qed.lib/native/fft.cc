// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
#include <cassert>
#include <cmath>
#include <complex>
#include <fstream>
#include <limits>
#include <numbers>
#include <random>
#include <string>
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


// the side of the rasters whose spectra are written out for inspection
constexpr int side = 128;


// make a square raster of the plane wave with the frequency {k0} along the lines and {k1} along
// the samples, in cycles across the raster; frequencies between whole numbers fall between bins
static auto
plane(double k0, double k1) -> grid_t
{
    // make the grid
    auto grid = grid_t { packing_t(shape_t { side, side }), storage_t { side * side } };
    // go through its cells
    for (auto idx : grid.packing()) {
        // the phase of the wave at this cell
        auto phase = 2 * std::numbers::pi * (k0 * idx[0] + k1 * idx[1]) / side;
        // set the cell
        grid[idx] = std::complex<float>(std::cos(phase), std::sin(phase));
    }
    // hand it off
    return grid;
}


// make a square raster of complex noise whose spectrum fills the frequencies within {h0} of
// {c0} along the lines and within {h1} of {c1} along the samples, and nothing else; the whole
// spectrum when the band covers it
static auto
noise(int c0, int h0, int c1, int h1) -> grid_t
{
    // a generator with a fixed seed, so the pictures are the same every time
    auto generator = std::mt19937(1998);
    // and the distribution of the parts of each frequency
    auto gauss = std::normal_distribution<float>(0, 1);
    // make the spectrum
    auto spectrum = grid_t { packing_t(shape_t { side, side }), storage_t { side * side } };
    // go through its frequencies
    for (auto idx : spectrum.packing()) {
        // the signed frequency of this cell along each axis
        auto k0 = idx[0] < side / 2 ? idx[0] : idx[0] - side;
        auto k1 = idx[1] < side / 2 ? idx[1] : idx[1] - side;
        // whether it falls in the band
        auto inside = std::abs(k0 - c0) <= h0 && std::abs(k1 - c1) <= h1;
        // a frequency in the band gets a random amplitude and phase; the rest get nothing
        spectrum[idx] = inside ? std::complex<float>(gauss(generator), gauss(generator)) : 0;
    }
    // the samples with that spectrum are its inverse transform, which is the conjugate of the
    // forward transform of its conjugate; the overall scale does not matter here
    for (auto idx : spectrum.packing()) {
        // conjugate going in
        spectrum[idx] = std::conj(spectrum[idx]);
    }
    // transform
    auto samples = qed::native::fft(spectrum);
    // and conjugate coming out
    for (auto idx : samples.packing()) {
        // one cell at a time
        samples[idx] = std::conj(samples[idx]);
    }
    // hand it off
    return samples;
}


// write the spectrum of {raster}, tapered first if asked to, to the file {name}
static auto
emit(const std::string & name, grid_t raster, bool taper) -> void
{
    // if asked to
    if (taper) {
        // taper the raster first
        qed::native::hann(raster);
    }
    // render its spectrum over sixty decibels
    auto tile = qed::native::channels::spectrum(qed::native::fft(raster), 60);
    // open the file
    auto stream = std::ofstream(name, std::ios::out | std::ios::binary);
    // and write the tile into it
    stream.write(reinterpret_cast<const char *>(tile.data()), tile.bytes());
    // all done
    return;
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

    // a wave with a few of its samples marked as fill, the way a region at the edge of a swath is
    auto marked = wave(2, 1);
    marked[index_t { 0, 0 }] = std::complex<float>(std::nanf(""), std::nanf(""));
    marked[index_t { 5, 3 }] = std::complex<float>(std::numeric_limits<float>::infinity(), 0);
    // has the marks cleared
    qed::native::zeroNonFinite(marked);
    assert((marked[index_t { 0, 0 }] == std::complex<float>(0, 0)));
    assert((marked[index_t { 5, 3 }] == std::complex<float>(0, 0)));
    // while the rest of the wave is untouched
    assert(std::abs(marked[index_t { 1, 1 }] - wave(2, 1)[index_t { 1, 1 }]) < 1e-6);
    // so its spectrum still peaks at the frequency of the wave
    auto survivor = qed::native::fft(marked);
    // the strongest frequency
    auto strongest = index_t { 0, 0 };
    // go through them
    for (auto idx : survivor.packing()) {
        // and keep the brightest
        if (std::abs(survivor[idx]) > std::abs(survivor[strongest])) {
            // by remembering where it is
            strongest = idx;
        }
    }
    // which is the frequency of the wave
    assert(strongest == (index_t { 2, 1 }));

    // a raster with nothing in it, like a region the product has no samples for
    auto empty = qed::native::fft(wave(0, 0));
    // go through its cells
    for (auto idx : empty.packing()) {
        // and silence each one
        empty[idx] = 0;
    }
    // renders black throughout
    auto dark = qed::native::channels::spectrum(empty, 60);
    // go through its pixels
    for (auto line = 0; line < lines; ++line) {
        for (auto sample = 0; sample < samples; ++sample) {
            // each one is black
            assert(gray(dark, line, sample) == 0);
        }
    }

    // write out the spectra worth looking at, beside the test: a wave on a bin is a single dot,
    // offset from the center by its frequency
    emit("fft-wave.bmp", plane(10, 25), false);
    // a wave between bins leaks into a cross along both axes
    emit("fft-between.bmp", plane(10.5, 25.5), false);
    // which the taper gathers back into a compact blob
    emit("fft-between-hann.bmp", plane(10.5, 25.5), true);
    // noise fills the whole spectrum evenly, grain and all
    emit("fft-noise.bmp", noise(0, side, 0, side), false);
    // and noise limited to a band, off center along the lines, is what the spectrum of an slc
    // looks like: the band of the radar across the samples, its processed doppler band, offset
    // by the doppler centroid, along the lines
    emit("fft-slc.bmp", noise(-20, 35, 0, 50), false);

    // all done
    return 0;
}


// end of file
