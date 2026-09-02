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

// a level under construction, as a builder writes it
//
// the file has the layout a {Level} reads, but is mapped writable and carries no occupancy
// record: which tiles were written is the business of whoever hands out the work, since it
// is the one that knows when a level is complete. a draft is created once, at its full
// padded size, by the process that owns the level, and every worker that then writes tiles
// into it touches only the slots of the tiles it was given; the slots are disjoint by
// construction, so there is no lock and nothing to coordinate
template <class cellT>
class qed::pyramid::Draft {
    // types
public:
    // my cell
    using cell_type = cellT;
    // the layout of my file
    using packing_type = packing_t;
    // the file itself, mapped writable
    using storage_type = pyre::memory::map_t<cell_type>;
    // and the grid that lays the one over the other
    using grid_type = pyre::grid::grid_t<packing_type, storage_type>;
    // indices and shapes
    using index_type = typename packing_type::index_type;
    using shape_type = typename packing_type::shape_type;
    // file names
    using uri_type = uri_t;

    // metamethods
public:
    // take hold of the level in {tiles}, given the {shape} of the level and the {tile} it is
    // diced into; the file must already exist at its full size
    inline Draft(const uri_type & tiles, const shape_type & shape, const shape_type & tile);

    // a draft is a handle on a mapping, and copies freely
    Draft(const Draft &) = default;
    Draft(Draft &&) = default;
    Draft & operator=(const Draft &) = default;
    Draft & operator=(Draft &&) = default;
    // destructor
    ~Draft() = default;

    // interface
public:
    // make the file for a level of the given {shape} diced into {tile}, at its full padded
    // size, with no tile written; the file is sparse, so this costs nothing until tiles
    // land. a file that already exists starts over
    static inline auto create(
        const uri_type & tiles, const shape_type & shape, const shape_type & tile) -> void;

    // my extent
    inline auto shape() const -> shape_type;
    // the extent of one of my tiles
    inline auto tile() const -> shape_type;
    // the extent of my grid of tiles
    inline auto tiles() const -> shape_type;
    // deposit the dense {data} with its first cell at {origin}; cells that would land
    // outside my extent are dropped, so an edge tile may be handed over at full shape
    template <class gridT>
    inline auto write(const typename gridT::index_type & origin, const gridT & data) -> void;

    // data
private:
    // my cells
    grid_type _grid;
};

// the inline definitions
#include "Draft.icc"

// end of file
