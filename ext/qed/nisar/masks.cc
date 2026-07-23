// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for mask visualization pipelines
void
qed::py::nisar::masks(py::module & m)
{
    // create the {masks} submodule
    auto masks = m.def_submodule(
        // the name of the module
        "masks",
        // its docstring
        "support for nisar {mask} datasets");

    // the nisar kernels read a tile out of an h5 dataset (using {datatype} for the on-disk layout)
    // into a grid of a fixed cell type, then render it
    using grid_t = heapgrid_t<uint8_t>;

    // render a gcov mask tile
    masks.def(
        // the name
        "gcov",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride) -> bmp_t {
            // read the tile and render it
            return qed::nisar::masks::gcov<grid_t>(
                source, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride));
        },
        // the signature
        "source"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a,
        // the docstring
        "render a gcov mask tile");

    // render a gunw mask tile
    masks.def(
        // the name
        "gunw",
        // the handler
        [](const dataset_t & source, const datatype_t & datatype,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride) -> bmp_t {
            // read the tile and render it
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


// end of file
