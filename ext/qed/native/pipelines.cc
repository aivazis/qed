// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for the pipelines assembled out of flow factories
void
qed::py::native::pipelines(py::module & m)
{
    // create a {pipelines} submodule
    auto pipelines = m.def_submodule(
        // the name of the module
        "pipelines",
        // its docstring
        "visualization pipelines assembled out of the factories of {pyre::flow}");

    // the value of a real tile, painted gray
    using value_t = qed::native::pipelines::Value;
    // make the class
    auto cls = py::class_<value_t>(
        // in this module
        pipelines,
        // the name
        "Value",
        // the docstring
        "the value of a real tile, painted gray, through flow factories");

    // the constructor
    cls.def(
        // the implementation
        py::init<>(),
        // the docstring
        "make a pipeline, whose graphs are built on first use");

    // render a tile
    cls.def(
        // the name
        "render",
        // the handler
        [](value_t & self, const py::buffer & source, const py::iterable & origin,
           const py::iterable & shape, const py::iterable & stride, double min,
           double max) -> py::bytes {
            // rebuild the tile geometry as rank-2 grid coordinates
            auto o = asIndex<2>(origin);
            auto t = asShape<2>(shape);
            auto s = asIndex<2>(stride);
            // dispatch on the buffer's cell type, as the channels do, and run the pipeline over the
            // tile; a foreign order buffer arrives as a native copy of the tile, so the geometry
            // the pipeline sees is the dispatcher's, not the caller's
            return onTile<
                2, char, int8_t, int16_t, int32_t, int64_t, uint8_t, uint16_t, uint32_t, uint64_t,
                float, double>(
                source, o, t, s,
                [&](const auto & grid, const auto & o, const auto & t, const auto & s) {
                    // render, and get a view of the encoded image
                    auto image = self.render(grid, o, t, s, min, max);
                    // copy its bytes, since the pipeline reuses the image for the next tile
                    return py::bytes(reinterpret_cast<const char *>(image.data()), image.cells());
                });
        },
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the tile of {source} at {origin}+{shape} with the given {stride}, mapping the "
        "values in [{min}, {max}] onto [0,1]");

    // all done
    return;
}


// end of file
