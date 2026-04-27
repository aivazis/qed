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
class qed::nisar::real::MaskedCoherence {
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
    // the normalizer
    using norm_type = parametric_t<source_iterator_type>;
    // the color map
    using colormap_type = gray_t<norm_type>;

    // metamethods
public:
    inline MaskedCoherence(
        source_const_reference data, mask_const_reference mask,
        // parameters
        double mi, double max);

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
    // the normalizer
    norm_type _normalizer;
    // the colormap
    colormap_type _color;

    // default metamethods
public:
    // destructor
    ~MaskedCoherence() = default;

    // constructors
    MaskedCoherence(const MaskedCoherence &) = default;
    MaskedCoherence(MaskedCoherence &&) = default;
    MaskedCoherence & operator=(const MaskedCoherence &) = default;
    MaskedCoherence & operator=(MaskedCoherence &&) = default;
};


// the definitions
#include "MaskedCoherence.icc"


// end of file
