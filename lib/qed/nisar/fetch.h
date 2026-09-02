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

// moving tiles between rasters of either kind
//
// every kernel here does the same first thing: gather a strided tile of its source into a
// dense grid, and only then look at the cells. the source used to be an hdf5 dataset and
// nothing else; now it may also be a level of a pyramid, a flat file of tiles the kernel
// reads through a mapping. these overloads are the one place that knows the difference, so
// the kernels can name their source by a template parameter and never ask what it is
namespace qed::nisar {
    // gather the tile at {origin}+{shape} of an hdf5 dataset, taking every {stride}-th cell
    // along each axis, into a fresh {gridT}; the {datatype} is the memory type the library
    // converts the cells to on the way
    template <class gridT>
    inline auto fetch(
        const dataset_t & source, const datatype_t & datatype,
        const typename gridT::index_type & origin, const typename gridT::shape_type & shape,
        const typename gridT::index_type & stride) -> gridT;

    // gather the same tile from a level of a pyramid; a level holds cells of one type only,
    // so the {datatype} an hdf5 read would convert to has no bearing on it
    template <class gridT, class cellT>
    inline auto fetch(
        const level_t<cellT> & source, const datatype_t &,
        const typename gridT::index_type & origin, const typename gridT::shape_type & shape,
        const typename gridT::index_type & stride) -> gridT;

    // place the dense {data} in a draft of a pyramid level with its first cell at {origin}; the
    // draft has its own idea of the cell type, so the {datatype} has no bearing on it
    template <class gridT, class cellT>
    inline auto deposit(
        draft_t<cellT> & destination, const datatype_t &, const typename gridT::index_type & origin,
        const gridT & data) -> void;
}    // namespace qed::nisar

// the inline definitions
#include "fetch.icc"

// end of file
