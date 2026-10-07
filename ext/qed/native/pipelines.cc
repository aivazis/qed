// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// the bindings of the pipelines over one cell type
namespace qed::py::native {
    // bind the amplitude pipeline over complex cells of type {cellT} in {cell}
    template <class cellT>
    inline void bindAmplitude(py::module & cell)
    {
        // the pipeline
        using amplitude_t = qed::native::pipelines::Amplitude<cellT>;
        // make the class
        auto cls = py::class_<amplitude_t>(
            // in this module
            cell,
            // the name
            "Amplitude",
            // the docstring
            "the amplitude of a complex tile, painted gray, through flow factories");

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
            [](amplitude_t & self, const py::buffer & source, const py::iterable & origin,
               const py::iterable & shape, const py::iterable & stride, double min,
               double max) -> py::bytes {
                // rebuild the tile geometry as rank-2 grid coordinates
                auto o = asIndex<2>(origin);
                auto t = asShape<2>(shape);
                auto s = asIndex<2>(stride);
                // dispatch on the buffer's cell type, which must be mine, and run the pipeline
                // over the tile
                return onTile<2, cellT>(
                    source, o, t, s,
                    [&](const auto & grid, const auto & o, const auto & t, const auto & s) {
                        // render, and get a view of the encoded image
                        auto image = self.render(grid, o, t, s, min, max);
                        // copy its bytes, since the pipeline reuses the image for the next tile
                        return py::bytes(
                            reinterpret_cast<const char *>(image.data()), image.cells());
                    });
            },
            // the signature
            "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
            // the docstring
            "render the tile of {source} at {origin}+{shape} with the given {stride}, mapping "
            "the magnitudes in [{min}, {max}] onto [0,1]");

        // all done
        return;
    }
    // bind the complex pipeline over complex cells of type {cellT} in {cell}
    template <class cellT>
    inline void bindComplex(py::module & cell)
    {
        // the pipeline
        using complex_t = qed::native::pipelines::Complex<cellT>;
        // make the class
        auto cls = py::class_<complex_t>(
            // in this module
            cell,
            // the name
            "Complex",
            // the docstring
            "a complex tile, painted in color, through flow factories");

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
            [](complex_t & self, const py::buffer & source, const py::iterable & origin,
               const py::iterable & shape, const py::iterable & stride, double min, double max,
               double minPhase, double maxPhase, double saturation) -> py::bytes {
                // rebuild the tile geometry as rank-2 grid coordinates
                auto o = asIndex<2>(origin);
                auto t = asShape<2>(shape);
                auto s = asIndex<2>(stride);
                // dispatch on the buffer's cell type, which must be mine, and run the pipeline
                // over the tile
                return onTile<2, cellT>(
                    source, o, t, s,
                    [&](const auto & grid, const auto & o, const auto & t, const auto & s) {
                        // render, and get a view of the encoded image
                        auto image =
                            self.render(grid, o, t, s, min, max, minPhase, maxPhase, saturation);
                        // copy its bytes, since the pipeline reuses the image for the next tile
                        return py::bytes(
                            reinterpret_cast<const char *>(image.data()), image.cells());
                    });
            },
            // the signature
            "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a, "minPhase"_a,
            "maxPhase"_a, "saturation"_a,
            // the docstring
            "render the tile of {source} at {origin}+{shape} with the given {stride}, mapping "
            "the magnitudes in [{min}, {max}] onto the brightness and placing the phases in "
            "[{minPhase}, {maxPhase}] to make the hue, at the given {saturation}");

        // all done
        return;
    }

    // bind the pipelines over complex cells of type {cellT} in their own submodule
    template <class cellT>
    inline void bindComplexCell(py::module & m, const char * name, const char * doc)
    {
        // gather the pipelines of this cell type under its name, so a caller picks the one that
        // matches its raster
        auto cell = m.def_submodule(
            // the name of the cell type
            name,
            // its docstring
            doc);
        // the amplitude
        bindAmplitude<cellT>(cell);
        // and the complex value
        bindComplex<cellT>(cell);
        // all done
        return;
    }
} // namespace qed::py::native


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

    // the pipelines of complex tiles, over each of the complex cell types
    bindComplexCell<std::complex<float>>(
        pipelines, "complex64", "the pipelines over single precision complex cells");
    bindComplexCell<std::complex<double>>(
        pipelines, "complex128", "the pipelines over double precision complex cells");

    // all done
    return;
}


// end of file
