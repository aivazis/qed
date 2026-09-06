// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once


// the grid aliases these helpers build on
#include "external.h"
// what the implementations need
#include <bit>
#include <optional>
#include <string>
#include <tuple>
#include <utility>
#include <vector>


// support for consuming pyre's type-erased grid: every grid the python side builds presents as a
// buffer, and these helpers rebuild a read-only typed grid over that buffer and dispatch on its
// cell type, so one wrapper stands in for the old per-cell-type overload pile
namespace qed::py {
    // interpret a python buffer as a read-only grid of rank {dim} and cell type {cellT}, its
    // extents read from the buffer's own shape, laid over the block the buffer exports
    template <typename cellT, int dim>
    auto asGrid(const py::buffer_info & info) -> viewgrid_t<cellT, dim>;

    // interpret any python iterable (tuple, list, generator, ...) as a grid index of rank {dim}
    template <int dim>
    auto asIndex(const py::iterable & seq) -> pyre::grid::index_t<dim>;

    // interpret any python iterable (tuple, list, generator, ...) as a grid shape of rank {dim}
    template <int dim>
    auto asShape(const py::iterable & seq) -> pyre::grid::shape_t<dim>;

    // dispatch on a python buffer's cell format across the candidate cell types {cellTs}: rebuild
    // a read-only grid of rank {dim} over the buffer's block and hand it to {f}, whichever cell
    // type matched; a buffer in a byte order other than the host's is refused
    template <int dim, typename... cellTs, typename F>
    auto onGrid(const py::buffer & source, F && f);
    // split a buffer's struct code into the code of the scalar itself and whether its leading
    // byte order marker, if there is one, names the order the host lacks
    inline auto splitFormat(const std::string & format) -> std::pair<std::string, bool>;
    // run {f} over the tile at {origin}+{tile} with the given {stride} of the grid the buffer
    // {source} exports, dispatching on its cell type across {cellTs}; {f} is invoked as
    // {f(grid, origin, tile, stride)}: a buffer in the host's byte order is viewed in place, while
    // one in the other order has the footprint of the tile copied through the swap into a native
    // block first, so that {f} sees a tile that starts at the origin with unit stride and the
    // kernels never meet a swapped cell
    template <int dim, typename... cellTs, typename F>
    auto onTile(
        const py::buffer & source, const pyre::grid::index_t<dim> & origin,
        const pyre::grid::shape_t<dim> & tile, const pyre::grid::index_t<dim> & stride, F && f);
    // the foreign order leg of {onTile}: copy the footprint of the tile through the swap and hand
    // {f} a native view over the copy
    template <typename cellT, int dim, typename F>
    auto swapTile(
        const py::buffer_info & info, const pyre::grid::index_t<dim> & origin,
        const pyre::grid::shape_t<dim> & tile, const pyre::grid::index_t<dim> & stride, F && f);
    // like {onGrid}, but a buffer in the byte order the host lacks yields a grid whose cells swap
    // on access, for kernels that visit arbitrary cells and can pay for the swap cell by cell
    template <int dim, typename... cellTs, typename F>
    auto onCells(const py::buffer & source, F && f);
}    // namespace qed::py


// the inline implementations
#include "grid.icc"


// end of file
