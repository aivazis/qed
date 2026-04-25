// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once


// externals
#include <array>
// support
#include <pyre/viz.h>


// map a single value to a shade of gray
template <class sourceT>
class qed::nisar::mask::RawMask {
    // types
public:
    // my template parameter
    using source_type = sourceT;
    // its reference type
    using source_const_reference = const source_type &;
    // and an iterator over its contents
    using iterator_type = typename source_type::const_iterator;

    // i generate {r,g,b} triplets
    using rgb_type = pyre::viz::rgb_t;
    // my palette
    using palette_type = std::array<rgb_type, 0xFF>;

    // metamethods
public:
    inline RawMask(source_const_reference data);

    // accessors
public:
    inline auto palette(int code) const -> rgb_type;

    // mutators
public:
    inline auto palette(int code, rgb_type color) -> void;


    // interface: behave like an iterator
public:
    // map the current data value to a color
    inline auto operator*() const -> rgb_type;
    // get the next value from the source; only support the prefix form, if possible
    inline auto operator++() -> void;

    // implementation details: data
private:
    // the data source
    iterator_type _source;
    // the color palette
    palette_type _palette;

    // default metamethods
public:
    // destructor
    ~RawMask() = default;

    // constructors
    RawMask(const RawMask &) = default;
    RawMask(RawMask &&) = default;
    RawMask & operator=(const RawMask &) = default;
    RawMask & operator=(RawMask &&) = default;
};


// the definitions
#include "RawMask.icc"


// end of file
