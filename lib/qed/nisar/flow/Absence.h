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


// recolor the cells with no data: a cell whose magnitude is the {fill} the product declared turns
// faint brick red, a nan the product did not declare gets a color of its own, and every other cell
// keeps its color
template <class dataT, class colorT>
class qed::nisar::flow::Absence : public pyre::flow::protocols::Factory {
    // type aliases
public:
    // me
    using self_type = Absence<dataT, colorT>;
    // my superclass
    using super_type = pyre::flow::protocols::Factory;
    // my slots: the cells of the raster, and the color channels
    using data_type = dataT;
    using color_type = colorT;
    // the colors i paint
    using rgb_type = pyre::viz::rgb_t;
    // what a fill value is spelled as: the magnitude of the cell the product declared
    using fill_type = double;
    // the spelling of types
    using string_type = pyre::flow::string_t;

    // ref to me
    using factory_ref_type = std::shared_ptr<Absence>;
    // and to my products
    using data_ref_type = std::shared_ptr<data_type>;
    using color_ref_type = std::shared_ptr<color_type>;

    // the spelling of my type, and the descriptions of my slots and settings
public:
    // simulate my c++ declaration
    static inline auto declSelf() -> string_type;
    // the human readable form of my class name
    static inline auto className() -> string_type;
    // the descriptions of my slots, shared by every factory of my type
    static inline auto declSlots() -> const slots_type &;
    // the descriptions of my settings, shared by every factory of my type
    static inline auto declSettings() -> const settings_type &;

    // introspection
public:
    // the descriptions of my slots
    inline virtual auto slots() const -> const slots_type & override;
    // the descriptions of my settings
    inline virtual auto settings() const -> const settings_type & override;

    // factory
public:
    inline static auto create(
        const name_type & name = "", fill_type fill = std::numeric_limits<fill_type>::quiet_NaN())
        -> factory_ref_type;

    // metamethods
public:
    // destructor
    inline virtual ~Absence();
    // constructor; DON'T CALL
    inline Absence(sentinel_type, const name_type &, fill_type);

    // accessors
public:
    // the magnitude of the value the product declared as its fill
    inline auto fill() const -> fill_type;
    // the products bound to my input slots
    inline auto data() -> data_ref_type;
    inline auto red() -> color_ref_type;
    inline auto green() -> color_ref_type;
    inline auto blue() -> color_ref_type;
    // and to my output slots
    inline auto paintedRed() -> color_ref_type;
    inline auto paintedGreen() -> color_ref_type;
    inline auto paintedBlue() -> color_ref_type;

    // mutators
public:
    // change the fill
    inline auto fill(fill_type) -> factory_ref_type;

    // flow protocol
public:
    inline virtual auto make(const name_type & slot, super_type::product_ref_type product)
        -> super_type::factory_ref_type override;

    // implementation details - data
private:
    // the magnitude of the value the product declared as its fill
    fill_type _fill;

    // constants
private:
    // a cell holding exactly what the product declared it would write where it has nothing to
    // say; the masked channels paint their out-of-swath margin this faint brick red, so absence
    // looks the same whether a mask or the fill value announced it
    static constexpr rgb_type declared = { 0.10, 0.05, 0.05 };
    // a cell holding a nan the product never declared, which is a bug in whatever wrote it and
    // worth seeing rather than hiding
    static constexpr rgb_type undeclared = { 0.04, 0.11, 0.10 };

    // suppressed metamethods
private:
    // constructors
    Absence(const Absence &) = delete;
    Absence & operator=(const Absence &) = delete;
    Absence(Absence &&) = delete;
    Absence & operator=(Absence &&) = delete;
};

// get the inline definitions
#include "Absence.icc"


// end of file
