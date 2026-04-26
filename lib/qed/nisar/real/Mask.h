// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once


// forwarde declarations
#include "forward.h"
// externals
#include <array>
// support
#include <pyre/viz.h>


// map a single value to a shade of gray
template <class sourceT, class maskT>
class qed::nisar::real::Mask {
    // types
public:
    // my template parameters
    using source_type = sourceT;
    using mask_type = maskT;
    // their reference type
    using source_const_reference = const source_type &;
    using mask_const_reference = const mask_type &;
    // and iterators over their contents
    using source_iterator_type = typename source_type::const_iterator;
    using mask_iterator_type = typename mask_type::const_iterator;

    // type aliases for the workflow nodes
    // the phase selector
    using selector_type = parametric_t<source_iterator_type>;
    using scale_type = affine_t<selector_type>;
    // the color map
    using colormap_type = hl_t<scale_type, constant_t>;

    // metamethods
public:
    inline Mask(
        source_const_reference data, mask_const_reference mask,
        // parameters
        double mi, double max, double brightness);

    // interface: behave like an iterator
public:
    // map the current data value to a color
    inline auto operator*() const -> typename colormap_type::rgb_type;
    // get the next value from the source; only support the prefix form, if possible
    inline auto operator++() -> void;

    // implementation details: data
private:
    // the data source
    source_iterator_type _source;
    // the mask
    mask_iterator_type _mask;
    // the phase selector
    selector_type _selector;
    // scaling the hue
    scale_type _hue;
    // the brightness
    constant_t _brightness;
    // the colormap
    colormap_type _color;

    // default metamethods
public:
    // destructor
    ~Mask() = default;

    // constructors
    Mask(const Mask &) = default;
    Mask(Mask &&) = default;
    Mask & operator=(const Mask &) = default;
    Mask & operator=(Mask &&) = default;
};


// the definitions
#include "Mask.icc"


// end of file
