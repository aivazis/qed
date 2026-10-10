// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// external dependencies and the local type aliases
#include "../externals.h"
// the namespace and its forward declarations
#include "../forward.h"
// the local forward declarations
#include "forward.h"


// support
#include <pyre/flow.h>


// a raster over a dataset of a nisar product, or over a level of its pyramid: it holds no cells,
// only what a slicer needs to read a window of them, so it comes into a graph made by whoever
// opened the product, and is never stale
template <class sourceT, class cellT>
class qed::nisar::flow::Raster : public pyre::flow::protocols::Product {
    // type aliases
public:
    // me
    using self_type = Raster<sourceT, cellT>;
    // my superclass
    using super_type = pyre::flow::protocols::Product;
    // what i read: an hdf5 dataset, or a level of a pyramid
    using source_type = sourceT;
    // the type of the cells a window of me is read into
    using cell_type = cellT;
    // the memory type an hdf5 read converts the cells to on the way
    using datatype_type = datatype_t;

    // shared pointers to my instances
    using ref_type = std::shared_ptr<Raster>;
    // the spelling of types
    using string_type = pyre::flow::string_t;

    // the spelling of my type
public:
    // simulate my c++ declaration
    static inline auto declSelf() -> string_type;
    // the human readable form of my class name
    static inline auto className() -> string_type;

    // factory
public:
    inline static auto create(const name_type & name, source_type source, datatype_type datatype)
        -> ref_type;

    // metamethods
public:
    // destructor
    inline virtual ~Raster();
    // constructor; DON'T CALL
    inline Raster(sentinel_type, const name_type &, source_type, datatype_type);

    // accessors
public:
    // what i read
    inline auto source() const -> const source_type &;
    // the memory type of the cells
    inline auto datatype() const -> const datatype_type &;

    // implementation details - data
private:
    // what i read
    source_type _source;
    // the memory type of the cells
    datatype_type _datatype;

    // suppressed metamethods
private:
    // constructors
    Raster(const Raster &) = delete;
    Raster & operator=(const Raster &) = delete;
    Raster(Raster &&) = delete;
    Raster & operator=(Raster &&) = delete;
};

// get the inline definitions
#include "Raster.icc"


// end of file
