// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
#include <cassert>
#include <complex>
#include <algorithm>
#include <string>
#include <vector>
#include <pyre/journal.h>

// get the grid
#include <pyre/grid.h>


// type aliases
// we generate 2d canonically packed tiles
using packing_t = pyre::grid::canonical_t<2>;
// of single precision reals
using data_t = float;
// in file backed memory
using storage_t = pyre::memory::map_t<data_t>;
// to form a grid
using grid_t = pyre::grid::grid_t<packing_t, storage_t>;


// forward declarations
// override the default {shape} with the first two positional command line arguments, when present
static auto shapeFromCommandLine(int argc, char * argv[], grid_t::shape_type shape)
    -> grid_t::shape_type;


// build a dataset
int
main(int argc, char * argv[])
{
    // initialize the journal
    pyre::journal::init(argc, argv);
    pyre::journal::application("qed");

    // generate {data}, a discretization of the domain (-2,2) x (-2,2) into square,
    // face centered pixels such that {data[0,0]} is at the origin

    // first, set up the discretization
    // pick a default shape, large enough to exceed a typical display resolution
    grid_t::shape_type shape { 1964 * 2 + 1, 3024 * 2 + 1 };
    // let the command line override it
    shape = shapeFromCommandLine(argc, argv, shape);
    // center it
    grid_t::index_type origin { -shape / 2 };
    // layout
    packing_t packing { shape, origin };
    // storage
    storage_t map("r4.dat", packing.cells());
    // grid
    grid_t data { packing, map };

    // the pixel width is determined by the largest extent
    auto delta = 4.0f / (shape.max() - 1);

    // here is the transform that converts an index into a position in the complex plane
    auto project = [delta](grid_t::index_type idx) -> std::complex<data_t> {
        // transform
        auto scaled = delta * idx;
        // convert into a point in the complex plane
        return std::complex<data_t> { scaled[0], scaled[1] };
    };

    // fill the grid
    for (auto idx : data.packing()) {
        // convert the indices into a point in the complex plane
        auto z = project(idx);
        // compute f(z)
        auto f = (z - 1.0f) / (z * z + z + 1.0f);
        // store its magnitude, so the real field inherits the pole and zero structure
        data[idx] = std::abs(f);
    }

    // all done
    return 0;
}


// override the default {shape} with the first two positional command line arguments, when present
static auto
shapeFromCommandLine(int argc, char * argv[], grid_t::shape_type shape) -> grid_t::shape_type
{
    // collect the positional arguments that follow the program name
    auto dims = std::vector<int> {};
    // by scanning the command line
    for (auto arg = 1; arg < argc; ++arg) {
        // grab the token
        auto token = std::string(argv[arg]);
        // journal configuration flags start with '-', so skip them
        if (!token.empty() && token.front() == '-') {
            continue;
        }
        // anything else is interpreted as a dimension
        dims.push_back(std::stoi(token));
    }
    // if the user supplied both a row and a column count
    if (dims.size() >= 2) {
        // build the shape from them
        shape = grid_t::shape_type { dims[0], dims[1] };
    }
    // return the resolved shape
    return shape;
}


// end of file
