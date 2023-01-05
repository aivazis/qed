// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved

// code guard
#if !defined(qed_native_externals_h)
#define qed_native_externals_h


// STL
#include <tuple>
#include <vector>


// journal
#include <pyre/journal.h>
// pyre
#include <pyre/grid.h>
#include <pyre/viz.h>

// type aliases
namespace qed::native {
    // encodings
    using bmp_t = pyre::viz::bmp_t;

    // color maps
    // complex values
    template <typename sourceT>
    using complex_t = pyre::viz::colormaps::complex_t<sourceT>;
    // grayscale
    template <typename sourceT>
    using gray_t = pyre::viz::colormaps::gray_t<sourceT>;
    // hl
    template <typename hueSourceT, typename luminositySourceT>
    using hl_t = pyre::viz::colormaps::hl_t<hueSourceT, luminositySourceT>;
    // hsb
    template <typename hueSourceT, typename saturationSourceT, typename brightnessSourceT>
    using hsb_t = pyre::viz::colormaps::hsb_t<hueSourceT, saturationSourceT, brightnessSourceT>;
    // hsl
    template <typename hueSourceT, typename saturationSourceT, typename luminositySourceT>
    using hsl_t = pyre::viz::colormaps::hsl_t<hueSourceT, saturationSourceT, luminositySourceT>;

    // filters
    // map [0,1] to an interval
    template <typename sourceT>
    using affine_t = pyre::viz::filters::affine_t<sourceT>;
    // the amplitude of a complex source
    template <typename sourceT>
    using amplitude_t = pyre::viz::filters::amplitude_t<sourceT>;
    // a supplier of a constant value
    using constant_t = pyre::viz::filters::constant_t<double>;
    // map phase to [0,1]
    template <typename sourceT>
    using cycle_t = pyre::viz::filters::cycle_t<sourceT>;
    // support for zooming
    template <typename sourceT>
    using decimate_t = pyre::viz::filters::decimate_t<sourceT>;
    // extract the imaginary paty of a complex source
    template <typename sourceT>
    using imaginary_t = pyre::viz::filters::imaginary_t<sourceT>;
    // map a range of values to the unit interval
    template <typename sourceT>
    using parametric_t = pyre::viz::filters::parametric_t<sourceT>;
    // extract the real part of a complex source
    template <typename sourceT>
    using real_t = pyre::viz::filters::real_t<sourceT>;
}


#endif

// end of file
