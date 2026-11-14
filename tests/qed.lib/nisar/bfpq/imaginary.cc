// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
#include <algorithm>
#include <cassert>
#include <complex>
#include <cstddef>
#include <cstdint>
// pyre
#include <pyre/journal.h>
#include <pyre/h5.h>
#include <pyre/grid.h>
// the renderers under test, pulled in through the nisar umbrella
#include <qed/nisar.h>


// the imaginary part of a BFPQ encoded raster is drawn from the decoded values, exactly as the
// imaginary part of the same values stored as complex numbers would be; the samples are stored the
// way NISAR stores them, as a compound of two codes named {r} and {i}

// type aliases
// the decoded tile, as the bindings instantiate the kernel
using packing_t = pyre::grid::canonical_t<2>;
using grid_t = pyre::grid::grid_t<packing_t, pyre::memory::heap_t<std::complex<float>>>;
// the layout of the stored samples, independent of the cell type
struct stored_t {
    // the first code
    std::uint16_t r;
    // and the second
    std::uint16_t i;
};


// render a BFPQ encoded tile and compare it with the rendering of its decoded values
int
main(int argc, char * argv[])
{
    // initialize the journal
    pyre::journal::init(argc, argv);
    // attribute whatever gets logged to this test
    pyre::journal::application("bfpq.imaginary");

    // the tile is small and square
    const int side = 8;
    // the table maps each of these codes to a value
    const int codes = 16;
    // the range of values to render covers the whole table
    const double min = -20;
    const double max = 3 * (codes - 1) - 20;

    // build the lookup table, which spreads the codes over a range that has no part in common
    // with the codes themselves, so a tile drawn from the codes cannot pass for one drawn from
    // the values
    auto table = qed::nisar::bfpq_lut_layout_t { { codes } };
    auto lut = qed::nisar::bfpq_lut_t(table, table.cells());
    for (int code = 0; code < codes; ++code) {
        // each code stands for a value of its own
        lut[code] = 3.0f * code - 20.0f;
    }

    // fill the tile with samples whose two codes differ from each other and from cell to cell
    stored_t samples[side * side];
    for (int line = 0; line < side; ++line) {
        for (int sample = 0; sample < side; ++sample) {
            // make the pair of codes
            samples[line * side + sample] = stored_t {
                static_cast<std::uint16_t>((line * side + sample) % codes),
                static_cast<std::uint16_t>((line + 3 * sample) % codes),
            };
        }
    }

    // make the product
    pyre::h5::File file { "imaginary.h5", H5F_ACC_TRUNC, {}, {} };
    // its extent
    pyre::h5::DataSpace space { pyre::h5::shape_t { side, side } };
    // the stored layout: two codes named the way the files of the mission name them
    auto stored = pyre::h5::comptype_t(sizeof(stored_t));
    stored.insert("r", offsetof(stored_t, r), pyre::h5::datatype<std::uint16_t>());
    stored.insert("i", offsetof(stored_t, i), pyre::h5::datatype<std::uint16_t>());
    // make the dataset
    auto dataset = file.createDataSet(
        "samples", stored, space, pyre::h5::properties::DCPL(), pyre::h5::properties::DAPL());
    // and write the samples into it
    dataset.write(stored.id(), samples);

    // decode the samples by hand
    auto packing = packing_t { { side, side } };
    auto decoded = grid_t(packing, packing.cells());
    for (int line = 0; line < side; ++line) {
        for (int sample = 0; sample < side; ++sample) {
            // get the pair of codes
            auto pair = samples[line * side + sample];
            // and look each one up in the table
            decoded[{ line, sample }] = std::complex<float> { lut[pair.r], lut[pair.i] };
        }
    }

    // render the encoded tile; the kernel reads its samples lined up with the members of the file
    auto encoded = qed::nisar::bfpq::imaginary<grid_t>(
        dataset, lut, { 0, 0 }, { side, side }, { 1, 1 }, min, max);
    // render the decoded values
    auto expected =
        qed::native::channels::imaginary(decoded, { 0, 0 }, { side, side }, { 1, 1 }, min, max);

    // the two pictures are the same size
    assert((encoded.bytes() == expected.bytes()));
    // and hold the same pixels
    assert((std::equal(encoded.data(), encoded.data() + encoded.bytes(), expected.data())));

    // all done
    return 0;
}


// end of file
