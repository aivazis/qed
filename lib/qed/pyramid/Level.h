// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// external dependencies and the local type aliases
#include "externals.h"
// the namespace and its forward declarations
#include "forward.h"

// a decimated level of a raster, as a reader sees it
//
// a level is a flat file of tiles in packing order, every tile padded to the full tile
// shape, laid over by a chunked grid so that a cell's place in the file is arithmetic. the
// file is sparse: a tile the builder found nothing in was never written and occupies no
// disk, but a hole reads back as zero bytes rather than as the fill, and zero is a
// measurement. so the level carries an occupancy record naming the tiles that were actually
// written, and a read answers with the fill for any cell whose tile is not named, without
// touching the mapping at all. cells outside the extent of the level, i.e. in the padding
// of an edge tile, are fill for the same reason
template <class cellT>
class qed::pyramid::Level {
    // types
public:
    // me
    using self_type = Level<cellT>;
    // my cell
    using cell_type = cellT;
    // the layout of my file
    using packing_type = packing_t;
    // the file itself, mapped read only: many readers may hold a level at once
    using storage_type = pyre::memory::constmap_t<cell_type>;
    // and the grid that lays the one over the other
    using grid_type = pyre::grid::grid_t<packing_type, storage_type>;
    // the record of which of my tiles were written
    using occupancy_type = occupancy_t;
    // indices and shapes
    using index_type = typename packing_type::index_type;
    using shape_type = typename packing_type::shape_type;
    // file names
    using uri_type = uri_t;

    // metamethods
public:
    // take hold of the level in {tiles} whose written tiles are named in {occupancy}, given
    // the {shape} of the level, the {tile} it is diced into, and the {fill} that stands for
    // a cell nobody wrote
    inline Level(
        const uri_type & tiles, const uri_type & occupancy, const shape_type & shape,
        const shape_type & tile, cell_type fill);

    // a level is a handle on two mappings, and copies freely
    Level(const Level &) = default;
    Level(Level &&) = default;
    Level & operator=(const Level &) = default;
    Level & operator=(Level &&) = default;
    // destructor
    ~Level() = default;

    // interface
public:
    // my extent
    inline auto shape() const -> shape_type;
    // the extent of one of my tiles
    inline auto tile() const -> shape_type;
    // the extent of my grid of tiles
    inline auto tiles() const -> shape_type;
    // what a cell nobody wrote reads as
    inline auto fill() const -> cell_type;
    // whether the tile at {tile}, in tile coordinates, was written
    inline auto occupied(const index_type & tile) const -> bool;
    // whether the cell at {cell} lies within my extent and in a tile that was written
    inline auto holds(const index_type & cell) const -> bool;
    // gather into a fresh {gridT} the cells at {origin} and every {stride}-th cell after it
    // along each axis, {shape} of them per axis; the origin is in my own coordinates, the
    // way an hdf5 read takes it, and the caller scales it when it comes from a zoomed view
    template <class gridT>
    inline auto read(
        const typename gridT::index_type & origin, const typename gridT::shape_type & shape,
        const typename gridT::index_type & stride) const -> gridT;

    // implementation details
private:
    // verify that the two files are the size my layout says they must be
    inline auto _verify(const uri_type & tiles, const uri_type & occupancy) const -> void;

    // data
private:
    // my cells
    grid_type _grid;
    // the record of my written tiles
    occupancy_type _occupancy;
    // what stands for a cell nobody wrote
    cell_type _fill;
};

// the inline definitions
#include "Level.icc"

// end of file
