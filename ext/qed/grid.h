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
#include <optional>
#include <tuple>
#include <vector>


// support for consuming pyre's type-erased grid: every grid the python side builds presents as a
// buffer, and these helpers rebuild a read-only typed grid over that buffer and dispatch on its
// cell type, so one wrapper stands in for the old per-cell-type overload pile
namespace qed::py {
    // interpret a python buffer as a read-only grid of rank {dim} and cell type {cellT}, its
    // extents read from the buffer's own shape, laid over the block the buffer exports
    template <typename cellT, int dim>
    auto asGrid(const py::buffer_info & info) -> viewgrid_t<cellT, dim>;

    // interpret a python sequence as a grid index of rank {dim}
    template <int dim>
    auto asIndex(const std::vector<std::ptrdiff_t> & seq) -> pyre::grid::index_t<dim>;

    // interpret a python sequence as a grid shape of rank {dim}
    template <int dim>
    auto asShape(const std::vector<std::ptrdiff_t> & seq) -> pyre::grid::shape_t<dim>;

    // dispatch on a python buffer's cell format across the candidate cell types {cellTs}: rebuild
    // a read-only grid of rank {dim} over the buffer's block and hand it to {f}, whichever cell
    // type matched
    template <int dim, typename... cellTs, typename F>
    auto onGrid(const py::buffer & source, F && f);
} // namespace qed::py


// the inline implementations
#include "grid.icc"


// end of file
