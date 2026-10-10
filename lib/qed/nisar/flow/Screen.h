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


// recolor the cells a mask flags: the {ruleT} reads each mask code the way its product defines it,
// and either names a fixed color for the cell or lets it keep its color
template <class ruleT, class maskT, class colorT>
class qed::nisar::flow::Screen : public pyre::flow::protocols::Factory {
    // type aliases
public:
    // me
    using self_type = Screen<ruleT, maskT, colorT>;
    // my superclass
    using super_type = pyre::flow::protocols::Factory;
    // the reading of the mask
    using rule_type = ruleT;
    // my slots: the cells of the mask, and the color channels
    using mask_type = maskT;
    using color_type = colorT;
    // the colors i paint
    using rgb_type = typename rule_type::rgb_type;
    // the spelling of types
    using string_type = pyre::flow::string_t;

    // ref to me
    using factory_ref_type = std::shared_ptr<Screen>;
    // and to my products
    using mask_ref_type = std::shared_ptr<mask_type>;
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
    inline static auto create(const name_type & name = "") -> factory_ref_type;

    // metamethods
public:
    // destructor
    inline virtual ~Screen();
    // constructor; DON'T CALL
    inline Screen(sentinel_type, const name_type &);

    // accessors
public:
    // the products bound to my input slots
    inline auto mask() -> mask_ref_type;
    inline auto red() -> color_ref_type;
    inline auto green() -> color_ref_type;
    inline auto blue() -> color_ref_type;
    // and to my output slots
    inline auto paintedRed() -> color_ref_type;
    inline auto paintedGreen() -> color_ref_type;
    inline auto paintedBlue() -> color_ref_type;

    // flow protocol
public:
    inline virtual auto make(const name_type & slot, super_type::product_ref_type product)
        -> super_type::factory_ref_type override;

    // suppressed metamethods
private:
    // constructors
    Screen(const Screen &) = delete;
    Screen & operator=(const Screen &) = delete;
    Screen(Screen &&) = delete;
    Screen & operator=(Screen &&) = delete;
};

// get the inline definitions
#include "Screen.icc"


// end of file
