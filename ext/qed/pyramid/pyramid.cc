// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// externals
#include "external.h"
// namespace setup
#include "forward.h"


// the bindings of one cell type
namespace qed::py::pyramid {
    // present a shape as a python tuple
    template <class shapeT>
    inline auto asTuple(const shapeT & shape) -> py::tuple
    {
        // one entry per axis
        return py::make_tuple(shape[0], shape[1]);
    }

    // bind the level and the draft over cells of type {cellT} in their own submodule
    template <class cellT>
    inline void bindCell(py::module & m, const char * name, const char * doc)
    {
        // the level as a reader sees it, and as a builder writes it
        using level_type = level_t<cellT>;
        using draft_type = draft_t<cellT>;
        // the dense grid a read comes back in
        using grid_type = heapgrid_t<cellT>;
        // gather the two under the name of the cell type, spelled the way {qed.datatypes}
        // spells it, so a caller picks the pair that matches its raster
        auto cell = m.def_submodule(
            // the name
            name,
            // the docstring
            doc);

        // the level
        auto level = py::class_<level_type>(
            // the module
            cell,
            // the name
            "Level",
            // the docstring
            "a decimated level of a raster, as a reader sees it: a flat file of tiles under "
            "a chunked grid, and an occupancy record naming the tiles that were written");
        // the constructor
        level.def(
            // the implementation
            py::init([](const string_t & tiles, const string_t & occupancy,
                        const py::iterable & shape, const py::iterable & tile, cellT fill) {
                // take hold of the two files, given the layout
                return level_type(tiles, occupancy, asShape<2>(shape), asShape<2>(tile), fill);
            }),
            // the signature
            "tiles"_a, "occupancy"_a, "shape"_a, "tile"_a, "fill"_a,
            // the docstring
            "take hold of the level in {tiles} whose written tiles are named in {occupancy}, "
            "given its {shape}, the {tile} it is diced into, and the {fill} that stands for "
            "a cell nobody wrote");
        // the extent
        level.def_property_readonly(
            // the name
            "shape",
            // the implementation
            [](const level_type & self) -> py::tuple { return asTuple(self.shape()); },
            // the docstring
            "my extent");
        // the tile
        level.def_property_readonly(
            // the name
            "tile",
            // the implementation
            [](const level_type & self) -> py::tuple { return asTuple(self.tile()); },
            // the docstring
            "the extent of one of my tiles");
        // the grid of tiles
        level.def_property_readonly(
            // the name
            "tiles",
            // the implementation
            [](const level_type & self) -> py::tuple { return asTuple(self.tiles()); },
            // the docstring
            "the extent of my grid of tiles");
        // the fill
        level.def_property_readonly(
            // the name
            "fill",
            // the implementation
            [](const level_type & self) -> cellT { return self.fill(); },
            // the docstring
            "what a cell nobody wrote reads as");
        // the occupancy of a tile
        level.def(
            // the name
            "occupied",
            // the implementation
            [](const level_type & self, const py::iterable & tile) -> bool {
                // ask the record
                return self.occupied(asIndex<2>(tile));
            },
            // the signature
            "tile"_a,
            // the docstring
            "whether the tile at {tile}, in tile coordinates, was written");
        // whether a cell holds anything
        level.def(
            // the name
            "holds",
            // the implementation
            [](const level_type & self, const py::iterable & cell) -> bool {
                // check the extent and the record
                return self.holds(asIndex<2>(cell));
            },
            // the signature
            "cell"_a,
            // the docstring
            "whether the cell at {cell} lies within my extent and in a tile that was written");
        // a strided read
        level.def(
            // the name
            "read",
            // the implementation
            [](const level_type & self, const py::iterable & origin, const py::iterable & shape,
               const py::iterable & stride) -> py::array_t<cellT> {
                // the extent of the tile
                auto extent = asShape<2>(shape);
                // gather it
                auto data =
                    self.template read<grid_type>(asIndex<2>(origin), extent, asIndex<2>(stride));
                // make an array of the same extent
                auto array = py::array_t<cellT>(std::vector<py::ssize_t> { extent[0], extent[1] });
                // and hand the cells over
                std::copy(data.data(), data.data() + extent.cells(), array.mutable_data());
                // all done
                return array;
            },
            // the signature
            "origin"_a, "shape"_a, "stride"_a,
            // the docstring
            "gather into an array the cells at {origin} and every {stride}-th cell after it "
            "along each axis, {shape} of them per axis; the origin is in the level's own "
            "coordinates");

        // the draft
        auto draft = py::class_<draft_type>(
            // the module
            cell,
            // the name
            "Draft",
            // the docstring
            "a level under construction, as a builder writes it: the same file a level "
            "reads, mapped writable, with no occupancy record of its own");
        // the constructor
        draft.def(
            // the implementation
            py::init(
                [](const string_t & tiles, const py::iterable & shape, const py::iterable & tile) {
                    // take hold of the file, given the layout
                    return draft_type(tiles, asShape<2>(shape), asShape<2>(tile));
                }),
            // the signature
            "tiles"_a, "shape"_a, "tile"_a,
            // the docstring
            "take hold of the level in {tiles}, given its {shape} and the {tile} it is diced "
            "into; the file must already exist at its full size");
        // the creator
        draft.def_static(
            // the name
            "create",
            // the implementation
            [](const string_t & tiles, const py::iterable & shape, const py::iterable & tile) {
                // make the file
                draft_type::create(tiles, asShape<2>(shape), asShape<2>(tile));
                // all done
                return;
            },
            // the signature
            "tiles"_a, "shape"_a, "tile"_a,
            // the docstring
            "make the file for a level of {shape} diced into {tile}, at its full padded "
            "size and with no tile written; a file that already exists starts over");
        // the extent
        draft.def_property_readonly(
            // the name
            "shape",
            // the implementation
            [](const draft_type & self) -> py::tuple { return asTuple(self.shape()); },
            // the docstring
            "my extent");
        // the tile
        draft.def_property_readonly(
            // the name
            "tile",
            // the implementation
            [](const draft_type & self) -> py::tuple { return asTuple(self.tile()); },
            // the docstring
            "the extent of one of my tiles");
        // the grid of tiles
        draft.def_property_readonly(
            // the name
            "tiles",
            // the implementation
            [](const draft_type & self) -> py::tuple { return asTuple(self.tiles()); },
            // the docstring
            "the extent of my grid of tiles");
        // a deposit
        draft.def(
            // the name
            "write",
            // the implementation
            [](draft_type & self, const py::iterable & origin, const py::buffer & data) {
                // get the layout of the buffer
                auto info = data.request();
                // a buffer of the wrong rank cannot be a tile
                if (info.ndim != 2) {
                    // so complain
                    throw py::value_error("the data must be a two dimensional buffer");
                }
                // and neither can one of the wrong cell type
                if (info.format != py::format_descriptor<cellT>::format()) {
                    // so complain
                    throw py::value_error(
                        "the cell type of the data, '" + info.format + "', is not mine");
                }
                // the grid view assumes the cells are packed row by row
                if (info.strides[1] != info.itemsize
                    || info.strides[0] != info.itemsize * info.shape[1]) {
                    // so anything else is refused rather than misread
                    throw py::value_error("the data must be contiguous, row-major");
                }
                // deposit the tile
                self.write(asIndex<2>(origin), asGrid<cellT, 2>(info));
                // all done
                return;
            },
            // the signature
            "origin"_a, "data"_a,
            // the docstring
            "deposit the dense {data} with its first cell at {origin}; cells that would land "
            "outside my extent are dropped");
        // all done
        return;
    }
}    // namespace qed::py::pyramid


// the pyramid submodule
void
qed::py::pyramid::pyramid(py::module & m)
{
    // create the {pyramid} submodule
    auto pyramid = m.def_submodule(
        // the name of the module
        "pyramid",
        // its docstring
        "the pyramid storage: decimated levels as flat files of tiles, one pair of classes "
        "per cell type");
    // the integers, signed and unsigned; masks and classification rasters live here
    bindCell<std::int8_t>(pyramid, "int8", "levels of signed single byte integers");
    bindCell<std::uint8_t>(pyramid, "uint8", "levels of unsigned single byte integers");
    bindCell<std::int16_t>(pyramid, "int16", "levels of signed two byte integers");
    bindCell<std::uint16_t>(pyramid, "uint16", "levels of unsigned two byte integers");
    bindCell<std::int32_t>(pyramid, "int32", "levels of signed four byte integers");
    bindCell<std::uint32_t>(pyramid, "uint32", "levels of unsigned four byte integers");
    // the floating point numbers; the geocoded covariance, coherence and phase rasters
    bindCell<float>(pyramid, "float32", "levels of single precision reals");
    bindCell<double>(pyramid, "float64", "levels of double precision reals");
    // and the complex pairs; the single look complex products and the off diagonal
    // covariance terms
    bindCell<std::complex<float>>(pyramid, "complex64", "levels of single precision complex");
    bindCell<std::complex<double>>(pyramid, "complex128", "levels of double precision complex");
    // all done
    return;
}

// end of file
