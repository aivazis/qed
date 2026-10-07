// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// my class declaration
#include "Value.h"


// metamethods
qed::native::pipelines::Value::Value() : _graphs {} {}


qed::native::pipelines::Value::~Value()
{
    // go through my graphs
    for (auto & [shape, g] : _graphs) {
        // and take each one apart, so its parts can be released
        dismantle(g);
    }
    // all done
    return;
}


// implementation details
auto
qed::native::pipelines::Value::graph(int rows, int columns) -> graph_type &
{
    // the key of the graph
    auto key = std::make_pair(rows, columns);
    // look it up
    auto found = _graphs.find(key);
    // if it is there
    if (found != _graphs.end()) {
        // hand it off
        return found->second;
    }
    // otherwise, build it, file it, and hand it off
    return _graphs.emplace(key, build(rows, columns)).first->second;
}


auto
qed::native::pipelines::Value::build(int rows, int columns) -> graph_type
{
    // the shape of the tiles
    auto shape = shape_type(rows, columns);
    // the graph
    graph_type g;
    // the signal, which receives the decimated source
    g.signal = signal_type::create("signal", shape, 0.0);
    // the normalized values
    g.normalized = channel_type::create("normalized", shape, 0.0);
    // the color channels, one product each, so the colormap runs once per tile
    g.red = channel_type::create("red", shape, 0.0);
    g.green = channel_type::create("green", shape, 0.0);
    g.blue = channel_type::create("blue", shape, 0.0);
    // the encoded image
    g.image = image_type::create("image", shape);

    // make the normalizer
    g.normalizer = normalizer_type::create("normalizer");
    // it reads the signal
    g.normalizer->signal(g.signal);
    // and writes the normalized values
    g.normalizer->parametric(g.normalized);

    // make the colormap
    g.colormap = colormap_type::create("gray");
    // it reads the normalized values
    g.colormap->data(g.normalized);
    // and paints them into the red channel
    g.colormap->red(g.red);
    // the green one
    g.colormap->green(g.green);
    // and the blue one
    g.colormap->blue(g.blue);

    // make the codec
    g.codec = codec_type::create("bmp");
    // it reads the red channel
    g.codec->red(g.red);
    // the green one
    g.codec->green(g.green);
    // and the blue one
    g.codec->blue(g.blue);
    // and encodes them into the image
    g.codec->image(g.image);

    // hand off the graph
    return g;
}


auto
qed::native::pipelines::Value::dismantle(graph_type & g) -> void
{
    // the factories refer to their products and the products to their factories, so neither goes
    // away on its own; unhook the codec from the red channel
    g.codec->removeInput("red");
    // the green one
    g.codec->removeInput("green");
    // the blue one
    g.codec->removeInput("blue");
    // and the image
    g.codec->removeOutput("image");
    // unhook the colormap from the normalized values
    g.colormap->removeInput("data");
    // and the three channels
    g.colormap->removeOutput("red");
    g.colormap->removeOutput("green");
    g.colormap->removeOutput("blue");
    // unhook the normalizer from the signal
    g.normalizer->removeInput("signal");
    // and the normalized values
    g.normalizer->removeOutput("parametric");
    // all done
    return;
}


// end of file
