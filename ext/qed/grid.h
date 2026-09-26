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
#include <complex>
#include <optional>
#include <string>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>


// support for consuming pyre's type-erased grid: every grid the python side builds presents as a
// buffer, and these helpers rebuild a read-only typed grid over that buffer and dispatch on its
// cell type, so one wrapper stands in for the old per-cell-type overload pile
namespace qed::py {
    // interpret a python buffer as a read-only grid of rank {dim} and cell type {cellT}, its
    // extents and strides read from the buffer's own description, laid over the block the
    // buffer exports; a strided buffer, such as one band of a multi-band product, is honored
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
    // type holds its cells; a buffer in a byte order other than the host's is refused
    template <int dim, typename... cellTs, typename F>
    auto onGrid(const py::buffer & source, F && f);
    // split a buffer's struct code into the code of the scalar itself and whether its leading
    // byte order marker, if there is one, names the order the host lacks
    inline auto splitFormat(const std::string & format) -> std::pair<std::string, bool>;

    // the kinds of scalar a buffer can hold, as far as picking a cell type is concerned
    enum class scalar_t { signedInteger, unsignedInteger, floating, complex, other };
    // the kind of scalar the struct {code} of a buffer describes
    inline auto kindOf(const std::string & code) -> scalar_t;
    // the kind of scalar the cell type {cellT} is
    template <typename cellT>
    constexpr auto kindOf() -> scalar_t;
    // whether a buffer whose scalar has struct {code} and occupies {itemsize} bytes holds cells
    // of type {cellT}: the struct module has more than one code for the same integer, e.g. both
    // 'l' and 'q' are eight byte signed integers on most hosts, and which one a producer picks
    // is its own business, so the kind and the size decide rather than the spelling
    template <typename cellT>
    auto holds(const std::string & code, py::ssize_t itemsize) -> bool;
    // pick the candidate among {cellTs} that holds the cells of a buffer with scalar {code} of
    // {itemsize} bytes, and return what {g} makes of it; {g} is called with the tag
    // {std::type_identity<cellT>} of the winner. a candidate whose descriptor spells the code
    // exactly wins over one that merely holds the same kind and size, so a buffer never lands
    // on a different kernel than its spelling names; {format} is the buffer's full struct
    // code, for the complaint when nothing fits
    template <typename... cellTs, typename G>
    auto dispatch(
        const std::string & code, py::ssize_t itemsize, const std::string & format, G && g);
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
