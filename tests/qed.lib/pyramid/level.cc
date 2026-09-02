// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// support
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <limits>
#include <vector>
// pyre
#include <pyre/journal.h>
#include <pyre/grid.h>
#include <pyre/memory.h>
// the storage under test
#include <qed/pyramid.h>

// type aliases
// the cell
using cell_t = float;
// the level as a reader sees it, and as a builder writes it
using level_t = qed::pyramid::level_t<cell_t>;
using draft_t = qed::pyramid::draft_t<cell_t>;
// the dense grids that go in and come out
using packing_t = pyre::grid::canonical_t<2>;
using storage_t = pyre::memory::heap_t<cell_t>;
using grid_t = pyre::grid::grid_t<packing_t, storage_t>;
// indices and shapes
using index_t = level_t::index_type;
using shape_t = level_t::shape_type;

// the value a written cell at {row},{col} carries, so a cell says where it came from
static auto
stamp(long row, long col) -> cell_t
{
    // rows in the hundreds, columns in the units
    return static_cast<cell_t>(100 * row + col);
}

// make a dense grid of the given {shape} whose cells are stamped as if placed at {origin}
static auto
block(const index_t & origin, const shape_t & shape) -> grid_t
{
    // make the grid
    auto data = grid_t { packing_t { shape }, storage_t { shape.cells() } };
    // go through its cells
    for (auto idx : data.packing()) {
        // and stamp each one with where it will land
        data[idx] = stamp(origin[0] + idx[0], origin[1] + idx[1]);
    }
    // hand it off
    return data;
}

// write the occupancy record for a grid of {tiles} tiles, naming the given {written} ones
static auto
occupy(const std::string & uri, const shape_t & tiles, const std::vector<index_t> & written) -> void
{
    // one byte per tile, nothing written
    auto record = std::vector<std::uint8_t>(tiles.cells(), 0);
    // go through the written tiles
    for (const auto & tile : written) {
        // and mark each one, in tile order
        record[tile[0] * tiles[1] + tile[1]] = 1;
    }
    // open the file
    auto file = std::ofstream(uri, std::ofstream::binary);
    // deposit the record
    file.write(reinterpret_cast<const char *>(record.data()), record.size());
    // all done
    return;
}

// build a small sparse level through a draft, read it back through a level, and check that
// written cells come back as written, that unwritten tiles and the padding of edge tiles
// come back as fill, and that strided reads land on the right cells
int
main(int argc, char * argv[])
{
    // initialize the journal
    pyre::journal::init(argc, argv);
    pyre::journal::application("qed");

    // the files
    const auto tiles = std::string("level.tiles");
    const auto occupancy = std::string("level.occupancy");
    // a level of 7x9 cells diced into 3x4 tiles: a 3x3 grid of tiles, with padding on both
    // trailing edges
    const auto shape = shape_t { 7, 9 };
    const auto tile = shape_t { 3, 4 };
    // what stands for a cell nobody wrote
    const auto fill = std::numeric_limits<cell_t>::quiet_NaN();

    // make the file at its full padded size
    draft_t::create(tiles, shape, tile);
    // take hold of it for writing
    auto draft = draft_t(tiles, shape, tile);
    // the layout must be what we asked for
    assert(draft.shape() == shape);
    assert(draft.tile() == tile);
    assert((draft.tiles() == shape_t { 3, 3 }));
    // write the interior tile at the origin, in full
    draft.write(index_t { 0, 0 }, block({ 0, 0 }, { 3, 4 }));
    // the edge tile in the middle row, handed over at full tile shape: its last three
    // columns fall in the padding and must be dropped
    draft.write(index_t { 3, 8 }, block({ 3, 8 }, { 3, 4 }));
    // the edge tile in the last row, handed over clipped to the extent
    draft.write(index_t { 6, 4 }, block({ 6, 4 }, { 1, 4 }));
    // name the tiles that were written
    occupy(occupancy, draft.tiles(), { { 0, 0 }, { 1, 2 }, { 2, 1 } });

    // take hold of the level for reading
    auto level = level_t(tiles, occupancy, shape, tile, fill);
    // the layout must match
    assert(level.shape() == shape);
    assert(level.tile() == tile);
    assert((level.tiles() == shape_t { 3, 3 }));
    // the occupancy record must be honored
    assert(level.occupied({ 0, 0 }));
    assert(level.occupied({ 1, 2 }));
    assert(level.occupied({ 2, 1 }));
    assert(!level.occupied({ 0, 1 }));
    assert(!level.occupied({ 1, 1 }));
    assert(!level.occupied({ 2, 2 }));
    // a cell in a written tile is held
    assert(level.holds({ 2, 3 }));
    assert(level.holds({ 5, 8 }));
    // a cell in an unwritten tile is not
    assert(!level.holds({ 0, 4 }));
    assert(!level.holds({ 3, 0 }));
    // nor is a cell outside the extent, however close to a written tile
    assert(!level.holds({ 3, 9 }));
    assert(!level.holds({ 7, 4 }));
    assert(!level.holds({ -1, 0 }));

    // read the whole level at unit stride
    auto whole = level.read<grid_t>({ 0, 0 }, shape, { 1, 1 });
    // go through its cells
    for (auto idx : whole.packing()) {
        // the value that came back
        auto value = whole[idx];
        // a cell in a written tile carries its stamp
        if (level.holds(idx)) {
            // exactly
            assert(value == stamp(idx[0], idx[1]));
        }
        // anything else is fill
        else {
            // which is a nan
            assert(std::isnan(value));
        }
    }
    // the specific cells worth naming: the corner of the first tile
    assert((whole[{ 2, 3 }] == stamp(2, 3)));
    // the column of the middle edge tile that lies within the extent
    assert((whole[{ 3, 8 }] == stamp(3, 8)));
    assert((whole[{ 5, 8 }] == stamp(5, 8)));
    // the clipped last row
    assert((whole[{ 6, 4 }] == stamp(6, 4)));
    assert((whole[{ 6, 7 }] == stamp(6, 7)));
    // and unwritten neighbors of all of them
    assert(std::isnan((whole[{ 0, 4 }])));
    assert(std::isnan((whole[{ 3, 7 }])));
    assert(std::isnan((whole[{ 6, 8 }])));

    // a strided read from the origin: every other cell along both axes
    auto strided = level.read<grid_t>({ 0, 0 }, { 4, 5 }, { 2, 2 });
    // its cells stand for the cells at twice their index
    assert((strided[{ 0, 0 }] == stamp(0, 0)));
    assert((strided[{ 0, 1 }] == stamp(0, 2)));
    assert((strided[{ 1, 1 }] == stamp(2, 2)));
    assert((strided[{ 3, 2 }] == stamp(6, 4)));
    assert((strided[{ 3, 3 }] == stamp(6, 6)));
    // and the unwritten tiles show through
    assert(std::isnan((strided[{ 0, 2 }])));
    assert(std::isnan((strided[{ 2, 0 }])));
    assert(std::isnan((strided[{ 3, 4 }])));

    // a strided read away from the origin, with different strides on the two axes: the
    // origin is in decimated coordinates, so the footprint starts at (3, 4)
    auto offset = level.read<grid_t>({ 1, 1 }, { 2, 2 }, { 3, 4 });
    // (3, 4) lies in an unwritten tile
    assert(std::isnan((offset[{ 0, 0 }])));
    // (3, 8) is the top of the middle edge tile
    assert((offset[{ 0, 1 }] == stamp(3, 8)));
    // (6, 4) is the start of the clipped last row
    assert((offset[{ 1, 0 }] == stamp(6, 4)));
    // (6, 8) lies in an unwritten tile
    assert(std::isnan((offset[{ 1, 1 }])));

    // a read whose footprint runs past the extent gets fill for the overhang, not the
    // padding of the edge tile and not a crash: the footprint starts at (3, 6) and reaches
    // column 9 and row 7
    auto overhang = level.read<grid_t>({ 1, 2 }, { 5, 4 }, { 3, 3 });
    // (3, 6) is in an unwritten tile
    assert(std::isnan((overhang[{ 0, 0 }])));
    // (3, 9) is past the last column
    assert(std::isnan((overhang[{ 0, 1 }])));
    // (6, 6) is written
    assert((overhang[{ 1, 0 }] == stamp(6, 6)));
    // (9, 6) is past the last row
    assert(std::isnan((overhang[{ 2, 0 }])));

    // clean up
    std::remove(tiles.c_str());
    std::remove(occupancy.c_str());
    // all done
    return 0;
}

// end of file
