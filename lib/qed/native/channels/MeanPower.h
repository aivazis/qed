// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// the pipeline node aliases and the containers my declarations lean on
#include "../externals.h"


// the mean-power filter and its tile generator
namespace qed::native::channels {
    // an N-ary filter that reduces a set of complex sources to their mean power, mean(|z|^2)
    template <typename sourceT>
    class MeanPower {
        // types
    public:
        // i wrap a homogeneous collection of these
        using source_type = sourceT;
        // and i report my reduction as a real
        using value_type = double;

        // metamethods
    public:
        // i am built from the set of sources i reduce
        inline MeanPower(std::vector<source_type> sources);

        // interface
    public:
        // hand out the mean power at my current position
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
        ~MeanPower() = default;
        // copy constructor
        MeanPower(const MeanPower &) = default;
        // copy assignment
        MeanPower & operator=(const MeanPower &) = default;
        // move constructor
        MeanPower(MeanPower &&) = default;
        // move assignment
        MeanPower & operator=(MeanPower &&) = default;
    };

    // assemble the lazy pipeline that renders the mean power of a set of complex sources as a tile
    template <typename sourceT>
    auto meanpower(
        // the sources to reduce
        const std::vector<sourceT> & sources,
        // where the tile starts
        typename sourceT::index_type origin,
        // how big the tile is
        typename sourceT::shape_type tile,
        // how much to decimate as we zoom out
        typename sourceT::index_type stride,
        // the range of powers that maps onto the full color scale
        double min, double max) -> bmp_t;
}


// the implementations
#include "MeanPower.icc"


// end of file
