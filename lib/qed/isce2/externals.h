// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved

// code guard
#if !defined(qed_isce2_externals_h)
#define qed_isce2_externals_h


// journal
#include <pyre/journal.h>
// pyre
#include <pyre/grid.h>
#include <pyre/viz.h>
// my native sibling
#include "../native.h"


// type aliases
namespace qed::isce2 {
    // encodings
    using bmp_t = pyre::viz::iterators::codecs::bmp_t;

    // color maps
    // complex values
    template <typename sourceT>
    using complex_t = pyre::viz::iterators::colormaps::complex_t<sourceT>;
    // grayscale
    template <typename sourceT>
    using gray_t = pyre::viz::iterators::colormaps::gray_t<sourceT>;
    // hl
    template <typename hueSourceT, typename luminositySourceT>
    using hl_t = pyre::viz::iterators::colormaps::hl_t<hueSourceT, luminositySourceT>;
    // hsb
    template <typename hueSourceT, typename saturationSourceT, typename brightnessSourceT>
    using hsb_t = pyre::viz::iterators::colormaps::hsb_t<hueSourceT, saturationSourceT, brightnessSourceT>;
    // hsl
    template <typename hueSourceT, typename saturationSourceT, typename luminositySourceT>
    using hsl_t = pyre::viz::iterators::colormaps::hsl_t<hueSourceT, saturationSourceT, luminositySourceT>;

    // filters
    // map [0,1] to an interval
    template <typename sourceT>
    using affine_t = pyre::viz::iterators::filters::affine_t<sourceT>;
    // the amplitude of a complex source
    template <typename sourceT>
    using amplitude_t = pyre::viz::iterators::filters::amplitude_t<sourceT>;
    // a power law filter on the amplitude of a complex source
    template <typename sourceT>
    using power_t = pyre::viz::iterators::filters::power_t<sourceT>;
    // a supplier of a constant value
    using constant_t = pyre::viz::iterators::filters::constant_t<double>;
    // map phase to [0,1]
    template <typename sourceT>
    using cycle_t = pyre::viz::iterators::filters::cycle_t<sourceT>;
    // support for zooming
    template <typename sourceT>
    using decimate_t = pyre::viz::iterators::filters::decimate_t<sourceT>;
    // extract the imaginary paty of a complex source
    template <typename sourceT>
    using imaginary_t = pyre::viz::iterators::filters::imaginary_t<sourceT>;
    // map a range of values to the unit interval
    template <typename sourceT>
    using parametric_t = pyre::viz::iterators::filters::parametric_t<sourceT>;
    // extract the real part of a complex source
    template <typename sourceT>
    using real_t = pyre::viz::iterators::filters::real_t<sourceT>;
}


#endif

// end of file
