// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// the pipeline node aliases and the containers my declarations lean on
#include "../externals.h"


// the coherence filter and its tile generator
namespace qed::native::channels {
    // an N-ary filter that computes the temporal coherence |Σz|/Σ|z| of a set of complex sources
    template <typename sourceT>
    class Coherence {
        // types
    public:
        // i wrap a homogeneous collection of these
        using source_type = sourceT;
        // and i report my reduction as a real in [0,1]
        using value_type = double;

        // metamethods
    public:
        // i am built from the set of sources i reduce
        inline Coherence(std::vector<source_type> sources);

        // interface
    public:
        // hand out the coherence at my current position
        inline auto operator*() const -> value_type;
        // step every one of my sources forward together
        inline auto operator++() -> void;

        // implementation details: data
    private:
        // the sources i reduce
        std::vector<source_type> _sources;

        // default metamethods
    public:
        // destructor
        ~Coherence() = default;
        // copy constructor
        Coherence(const Coherence &) = default;
        // copy assignment
        Coherence & operator=(const Coherence &) = default;
        // move constructor
        Coherence(Coherence &&) = default;
        // move assignment
        Coherence & operator=(Coherence &&) = default;
    };

    // assemble the lazy pipeline that renders the coherence of a set of complex sources as a tile
    template <typename sourceT>
    auto coherence(
        // the sources to reduce
        const std::vector<sourceT> & sources,
        // where the tile starts
        typename sourceT::index_type origin,
        // how big the tile is
        typename sourceT::shape_type tile,
        // how much to decimate as we zoom out
        typename sourceT::index_type stride,
        // the range of coherence values that maps onto the full color scale
        double min, double max) -> bmp_t;
}


// the implementations
#include "Coherence.icc"


// end of file
