// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// my dependencies
#include "forward.h"


// a complex tile, painted in color: the tile is decimated into a signal that keeps the cells of
// the source, and fans out into two branches that meet at {hsb}: {cycle} places the phase of
// each cell in an interval and {affine} maps it onto [0, 2pi] to make the hue, while
// {amplitude} computes the magnitude and {parametric} maps it onto [0,1] to make the
// brightness; a {constant} supplies the saturation, and {bmp} encodes the colors; the graph of
// factories and products for each tile shape is built once and kept, so a tile only refills the
// signal and sets the intervals, and the flow recomputes what that made stale
template <typename cellT>
class qed::native::pipelines::Complex {
    // type aliases
public:
    // me
    using self_type = Complex<cellT>;
    // the cells of the source
    using cell_type = cellT;
    // the layout of the tiles
    using packing_type = pyre::grid::canonical_t<2>;
    // the shape of a tile
    using shape_type = packing_type::shape_type;
    // an index into a tile
    using index_type = packing_type::index_type;
    // the signal holds the cells of the source as they are, so their phase and magnitude are
    // computed in the precision of the source, as the iterators compute them
    using signal_grid_type = pyre::grid::grid_t<packing_type, pyre::memory::heap_t<cell_type>>;
    using signal_type = pyre::flow::products::tile_t<signal_grid_type>;
    // the phases, hues, saturations, magnitudes, and colors are double precision, as the
    // iterators carry them into the encoder
    using real_grid_type = pyre::grid::grid_t<packing_type, pyre::memory::heap_t<double>>;
    using real_type = pyre::flow::products::tile_t<real_grid_type>;
    // the brightness is single precision, as the normalizer of the iterators makes it
    using channel_grid_type = pyre::grid::grid_t<packing_type, pyre::memory::heap_t<float>>;
    using channel_type = pyre::flow::products::tile_t<channel_grid_type>;
    // the encoded image
    using image_type = pyre::viz::products::images::bmp_t;
    // a view of its bytes
    using image_view_type = image_type::constview_type;
    // the factories of the phase branch
    using cycle_type = pyre::flow::factories::filters::cycle_t<signal_type, real_type>;
    using affine_type = pyre::flow::factories::filters::affine_t<real_type, real_type>;
    // the factories of the amplitude branch
    using selector_type = pyre::flow::factories::selectors::amplitude_t<signal_type, real_type>;
    using normalizer_type = pyre::flow::factories::filters::parametric_t<real_type, channel_type>;
    // the saturation
    using constant_type = pyre::flow::factories::filters::constant_t<real_type>;
    // the colormap, where the branches meet
    using colormap_type = pyre::viz::factories::colormaps::hsb_t<
        real_type, real_type, channel_type, real_type, real_type, real_type>;
    // the encoder
    using codec_type = pyre::viz::factories::codecs::bmp_t<real_type>;
    // an interval of values
    using interval_type = pyre::flow::interval_t;

    // the graph for one tile shape
    struct graph_type {
        // the products
        std::shared_ptr<signal_type> signal;
        std::shared_ptr<real_type> cycle;
        std::shared_ptr<real_type> hue;
        std::shared_ptr<real_type> saturation;
        std::shared_ptr<real_type> amplitude;
        std::shared_ptr<channel_type> brightness;
        std::shared_ptr<real_type> red;
        std::shared_ptr<real_type> green;
        std::shared_ptr<real_type> blue;
        std::shared_ptr<image_type> image;
        // the factories
        std::shared_ptr<cycle_type> cycler;
        std::shared_ptr<affine_type> scaler;
        std::shared_ptr<selector_type> selector;
        std::shared_ptr<normalizer_type> normalizer;
        std::shared_ptr<constant_type> constant;
        std::shared_ptr<colormap_type> colormap;
        std::shared_ptr<codec_type> codec;
    };
    // the graphs, by tile shape
    using graphs_type = std::map<std::pair<int, int>, graph_type>;

    // metamethods
public:
    // constructor
    Complex();
    // destructor
    ~Complex();

    // interface
public:
    // render the tile of {source} at {origin} with the given {shape} and {stride}, mapping the
    // magnitudes in [{min}, {max}] onto the brightness, placing the phases in [{minPhase},
    // {maxPhase}] to make the hue, at the given {saturation}, and return a view of the encoded
    // image, which stays valid until the next tile of the same shape
    template <typename sourceT>
    auto render(
        const sourceT & source, typename sourceT::index_type origin,
        typename sourceT::shape_type shape, typename sourceT::index_type stride, double min,
        double max, double minPhase, double maxPhase, double saturation) -> image_view_type;

    // implementation details
private:
    // the graph for tiles of the given shape, built on first use
    auto graph(int rows, int columns) -> graph_type &;
    // build the graph for tiles of the given shape
    static auto build(int rows, int columns) -> graph_type;
    // take a graph apart, so that its products and factories, which refer to each other, can be
    // released
    static auto dismantle(graph_type &) -> void;

    // data members
private:
    graphs_type _graphs;

    // suppressed metamethods
private:
    // a pipeline owns its graphs, which cannot be shared
    Complex(const Complex &) = delete;
    Complex & operator=(const Complex &) = delete;
    // nor moved, since the graphs are taken apart when the pipeline goes away
    Complex(Complex &&) = delete;
    Complex & operator=(Complex &&) = delete;
};


// get the inline definitions
#include "Complex.icc"


// end of file
