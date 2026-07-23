// -*- C++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for the nisar stack tile generators
void
qed::py::nisar::stack(py::module & m)
{
    // create the {stack} submodule
    auto stack = m.def_submodule(
        // the name of the module
        "stack",
        // its docstring
        "support for aggregate views over stacks of nisar datasets");

    // the stack kernels read a tile out of each of a pile of h5 datasets (using {datatype} for the
    // on-disk layout) into grids of a fixed cell type, then aggregate and render them
    using grid_t = heapgrid_t<std::complex<float>>;

    // render the mean power of a stack tile
    stack.def(
        // the name
        "meanpower",
        // the handler
        [](const std::vector<dataset_t> & sources, const datatype_t & datatype,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride, double min, double max) -> bmp_t {
            // read the tiles and render their mean power
            return qed::nisar::stack::meanpower<grid_t>(
                sources, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride), min,
                max);
        },
        // the signature
        "sources"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the mean power of a stack tile");

    // render the coherence of a stack tile
    stack.def(
        // the name
        "coherence",
        // the handler
        [](const std::vector<dataset_t> & sources, const datatype_t & datatype,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape,
           std::vector<std::ptrdiff_t> stride, double min, double max) -> bmp_t {
            // read the tiles and render their coherence
            return qed::nisar::stack::coherence<grid_t>(
                sources, datatype, asIndex<2>(origin), asShape<2>(shape), asIndex<2>(stride), min,
                max);
        },
        // the signature
        "sources"_a, "datatype"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the coherence of a stack tile");

    // compute the statistics of a stack tile
    stack.def(
        // the name
        "stats",
        // the handler
        [](const std::vector<dataset_t> & sources, const datatype_t & datatype,
           std::vector<std::ptrdiff_t> origin, std::vector<std::ptrdiff_t> shape) -> stats_t {
            // read the tiles and collect their statistics
            return qed::nisar::stack::stats<grid_t>(
                sources, datatype, asIndex<2>(origin), asShape<2>(shape));
        },
        // the signature
        "sources"_a, "datatype"_a, "origin"_a, "shape"_a,
        // the docstring
        "compute the statistics of a stack tile");

    // all done
    return;
}


// end of file
