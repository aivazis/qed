// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
#include "external.h"
// namespace setup
#include "forward.h"


// the flow nodes that bring the rasters of nisar products into pipelines
namespace qed::py::nisar {
    // the flow types
    using product_t = pyre::flow::product_t;
    using catalog_t = pyre::flow::catalog::catalog_t;
    // the cells the kernels read windows of nisar rasters into
    using c64_t = std::complex<float>;
    using f32_t = float;
    // the cells of masks: stored in bytes in a pyramid level, and read wide, whatever the width
    // of the codes on disk
    using u8_t = std::uint8_t;
    using u32_t = std::uint32_t;
    // the tiles a window lands in: the cells of complex rasters as they are, and the cells of
    // real ones in double precision, the way the pipelines over reals take them
    template <class cellT>
    using flowtile_t = pyre::flow::products::tile_t<
        pyre::grid::grid_t<pyre::grid::canonical_t<2>, pyre::memory::heap_t<cellT>>>;

    // the catalog of the nodes this extension was compiled with
    inline auto registry() -> catalog_t &
    {
        // the one catalog
        static catalog_t catalog;
        // hand it off
        return catalog;
    }

    // bind the raster of {cellT} over a {sourceT}, and register it and the slicer that reads it
    // into tiles of {tileCellT}
    template <class sourceT, class cellT, class tileCellT>
    inline void bindRaster(py::module & m, const char * name)
    {
        // the raster
        using raster_type = qed::nisar::flow::raster_t<sourceT, cellT>;
        // and the slicer that reads it
        using fetch_type = qed::nisar::flow::fetch_t<raster_type, flowtile_t<tileCellT>>;
        // register them with my catalog
        registry().registerProduct<raster_type>();
        registry().registerFactory<fetch_type>();
        // bind the raster
        auto cls = py::classh<raster_type, product_t>(
            // the scope
            m,
            // the name of the class
            name,
            // the docstring
            "a raster over a dataset of a nisar product, or over a level of its pyramid");
        // the spelling of its type, which is its key in the catalog
        cls.def_property_readonly_static(
            // the name
            "decl",
            // the implementation
            [](const py::object &) -> std::string { return raster_type::declSelf(); },
            // the docstring
            "the declaration of my type, which is my key in the catalog");
        // all done
        return;
    }
} // namespace qed::py::nisar


// the flow nodes
void
qed::py::nisar::flow(py::module & m)
{
    // make a module
    auto flow = m.def_submodule(
        // the name
        "flow",
        // the docstring
        "the flow nodes that bring the rasters of nisar products into pipelines");

    // the rasters over datasets, read into complex or real cells
    bindRaster<dataset_t, c64_t, c64_t>(flow, "DatasetRasterC64");
    bindRaster<dataset_t, f32_t, double>(flow, "DatasetRasterF32");
    // and over the levels of pyramids, which hold cells of one type
    bindRaster<level_t<c64_t>, c64_t, c64_t>(flow, "LevelRasterC64");
    bindRaster<level_t<f32_t>, f32_t, double>(flow, "LevelRasterF32");
    // the masks, over datasets and over the levels of their pyramids, read into wide cells
    bindRaster<dataset_t, u32_t, u32_t>(flow, "DatasetRasterU32");
    bindRaster<level_t<u8_t>, u32_t, u32_t>(flow, "LevelRasterU8");

    // the tiles the masks are read into, which pyre has no use for
    registry().registerProduct<flowtile_t<u32_t>>();
    // recolor the cells of rasters of reals with no data
    registry()
        .registerFactory<qed::nisar::flow::absence_t<flowtile_t<double>, flowtile_t<f32_t>>>();
    // and the cells the masks of the products flag
    registry()
        .registerFactory<qed::nisar::flow::gunw_screen_t<flowtile_t<u32_t>, flowtile_t<f32_t>>>();
    registry()
        .registerFactory<qed::nisar::flow::gcov_screen_t<flowtile_t<u32_t>, flowtile_t<f32_t>>>();

    // the catalog
    flow.def(
        // the name
        "catalog",
        // the implementation
        []() -> catalog_t & { return registry(); },
        // the catalog outlives every reference to it
        py::return_value_policy::reference,
        // the docstring
        "the catalog of the flow nodes of nisar products");

    // make a raster over a dataset
    flow.def(
        // the name
        "raster",
        // the implementation
        [](const dataset_t & source, const datatype_t & datatype, const std::string & cell,
           const std::string & name) -> std::shared_ptr<product_t> {
            // complex cells
            if (cell == "complex64") {
                // make the raster and hand it off
                return qed::nisar::flow::raster_t<dataset_t, c64_t>::create(name, source, datatype);
            }
            // real ones
            if (cell == "float32") {
                // make the raster and hand it off
                return qed::nisar::flow::raster_t<dataset_t, f32_t>::create(name, source, datatype);
            }
            // nothing else
            throw py::value_error("there are no rasters of '" + cell + "' cells");
        },
        // the signature
        "source"_a, "datatype"_a, "cell"_a, "name"_a,
        // the docstring
        "make a raster over the dataset {source}, whose windows are read as {cell} cells, "
        "converted on the way by the memory {datatype}");

    // make a raster over a level of a pyramid of complex cells
    flow.def(
        // the name
        "raster",
        // the implementation
        [](const level_t<c64_t> & source, const datatype_t & datatype, const std::string &,
           const std::string & name) -> std::shared_ptr<product_t> {
            // make the raster and hand it off
            return qed::nisar::flow::raster_t<level_t<c64_t>, c64_t>::create(
                name, source, datatype);
        },
        // the signature
        "source"_a, "datatype"_a, "cell"_a, "name"_a,
        // the docstring
        "make a raster over the pyramid level {source}");

    // and of real cells
    flow.def(
        // the name
        "raster",
        // the implementation
        [](const level_t<f32_t> & source, const datatype_t & datatype, const std::string &,
           const std::string & name) -> std::shared_ptr<product_t> {
            // make the raster and hand it off
            return qed::nisar::flow::raster_t<level_t<f32_t>, f32_t>::create(
                name, source, datatype);
        },
        // the signature
        "source"_a, "datatype"_a, "cell"_a, "name"_a,
        // the docstring
        "make a raster over the pyramid level {source}");

    // make a raster over the mask of a product
    flow.def(
        // the name
        "mask",
        // the implementation
        [](const dataset_t & source, const std::string & name) -> std::shared_ptr<product_t> {
            // make the raster, reading the codes wide, and hand it off
            return qed::nisar::flow::raster_t<dataset_t, u32_t>::create(
                name, source, pyre::h5::datatype<u32_t>());
        },
        // the signature
        "source"_a, "name"_a,
        // the docstring
        "make a raster over the mask {source}, whose windows are read as unsigned 32 bit codes");

    // and over a level of its pyramid
    flow.def(
        // the name
        "mask",
        // the implementation
        [](const level_t<u8_t> & source, const std::string & name) -> std::shared_ptr<product_t> {
            // make the raster and hand it off; a level has no use for the memory type
            return qed::nisar::flow::raster_t<level_t<u8_t>, u32_t>::create(
                name, source, pyre::h5::datatype<u32_t>());
        },
        // the signature
        "source"_a, "name"_a,
        // the docstring
        "make a raster over the pyramid level {source} of a mask");

    // all done
    return;
}


// end of file
