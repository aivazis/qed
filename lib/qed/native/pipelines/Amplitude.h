// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// my dependencies
#include "forward.h"


// the amplitude of a complex tile, painted gray: the tile is decimated into a signal that keeps
// the cells of the source, {amplitude} computes their magnitude, {parametric} maps it onto
// [0,1], {gray} paints it, and {bmp} encodes it; the graph of factories and products for each
// tile shape is built once and kept, so a tile only refills the signal and sets the interval,
// and the flow recomputes what that made stale
template <typename cellT>
class qed::native::pipelines::Amplitude {
    // type aliases
public:
    // me
    using self_type = Amplitude<cellT>;
    // the cells of the source
    using cell_type = cellT;
    // the layout of the tiles
    using packing_type = pyre::grid::canonical_t<2>;
    // the shape of a tile
    using shape_type = packing_type::shape_type;
    // an index into a tile
    using index_type = packing_type::index_type;
    // the signal holds the cells of the source as they are, so their magnitude is computed in the
    // precision of the source, as the iterators compute it
    using signal_grid_type = pyre::grid::grid_t<packing_type, pyre::memory::heap_t<cell_type>>;
    using signal_type = pyre::flow::products::tile_t<signal_grid_type>;
    // the magnitudes are double precision, as {pyre::flow::magnitude} makes them
    using amplitude_grid_type = pyre::grid::grid_t<packing_type, pyre::memory::heap_t<double>>;
    using amplitude_type = pyre::flow::products::tile_t<amplitude_grid_type>;
    // the normalized values and the color channels are single precision, as the iterators make them
    using channel_grid_type = pyre::grid::grid_t<packing_type, pyre::memory::heap_t<float>>;
    using channel_type = pyre::flow::products::tile_t<channel_grid_type>;
    // the encoded image
    using image_type = pyre::viz::products::images::bmp_t;
    // a view of its bytes
    using image_view_type = image_type::constview_type;
    // the factories
    using selector_type =
        pyre::flow::factories::selectors::amplitude_t<signal_type, amplitude_type>;
    using normalizer_type =
        pyre::flow::factories::filters::parametric_t<amplitude_type, channel_type>;
    using colormap_type = pyre::viz::factories::colormaps::gray_t<channel_type>;
    using codec_type = pyre::viz::factories::codecs::bmp_t<channel_type>;
    // the interval of values that is mapped onto [0,1]
    using interval_type = pyre::flow::interval_t;

    // the graph for one tile shape
    struct graph_type {
        // the products
        std::shared_ptr<signal_type> signal;
        std::shared_ptr<amplitude_type> amplitude;
        std::shared_ptr<channel_type> normalized;
        std::shared_ptr<channel_type> red;
        std::shared_ptr<channel_type> green;
        std::shared_ptr<channel_type> blue;
        std::shared_ptr<image_type> image;
        // the factories
        std::shared_ptr<selector_type> selector;
        std::shared_ptr<normalizer_type> normalizer;
        std::shared_ptr<colormap_type> colormap;
        std::shared_ptr<codec_type> codec;
    };
    // the graphs, by tile shape
    using graphs_type = std::map<std::pair<int, int>, graph_type>;

    // metamethods
public:
    // constructor
    Amplitude();
    // destructor
    ~Amplitude();

    // interface
public:
    // render the tile of {source} at {origin} with the given {shape} and {stride}, mapping the
    // magnitudes in [{min}, {max}] onto [0,1], and return a view of the encoded image, which
    // stays valid until the next tile of the same shape
    template <typename sourceT>
    auto render(
        const sourceT & source, typename sourceT::index_type origin,
        typename sourceT::shape_type shape, typename sourceT::index_type stride, double min,
        double max) -> image_view_type;

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
    Amplitude(const Amplitude &) = delete;
    Amplitude & operator=(const Amplitude &) = delete;
    // nor moved, since the graphs are taken apart when the pipeline goes away
    Amplitude(Amplitude &&) = delete;
    Amplitude & operator=(Amplitude &&) = delete;
};


// get the inline definitions
#include "Amplitude.icc"


// end of file
