// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// externals
#include "external.h"
// namespace setup
#include "forward.h"


// the masks kernels, bound once per kind of raster they can read
namespace qed::py::nisar {
    // bind the masks kernels over a source of type {rasterT}
    template <class rasterT>
    inline void bindMasks(py::module & masks)
    {
        // the grid the kernels read into
        using grid_t = heapgrid_t<uint8_t>;
        masks.def(
            // the name
            "gcov",
            // the handler
            [](const rasterT & source, const datatype_t & datatype, const py::iterable & origin,
               const py::iterable & shape, const py::iterable & stride) -> bmp_t {
                // gather the tile and render it
                return qed::nisar::masks::gcov<grid_t>(
                    source, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride));
            },
            // the signature
            "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a,
            // the docstring
            "render a gcov mask tile");
        masks.def(
            // the name
            "gunw",
            // the handler
            [](const rasterT & source, const datatype_t & datatype, const py::iterable & origin,
               const py::iterable & shape, const py::iterable & stride) -> bmp_t {
                // gather the tile and render it
                return qed::nisar::masks::gunw<grid_t>(
                    source, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride));
            },
            // the signature
            "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a,
            // the docstring
            "render a gunw mask tile");
        // all done
        return;
    }
}    // namespace qed::py::nisar


// masks
void
qed::py::nisar::masks(py::module & m)
{
    // create the masks submodule
    auto masks = m.def_submodule(
        // the name of the module
        "masks",
        // its docstring
        "support for nisar {mask} datasets");
    // the kernels over hdf5 datasets, the way the products are read
    bindMasks<dataset_t>(masks);
    // and over pyramid levels, the way a zoomed out view is read
    bindMasks<level_t<std::uint8_t>>(masks);
    // all done
    return;
}

// end of file
