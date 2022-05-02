// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// support
#include <cassert>
#include <complex>
#include <algorithm>
#include <pyre/journal.h>

// get the grid
#include <pyre/grid.h>


// type aliases
// we generate 2d canonically packed tiles
using packing_t = pyre::grid::canonical_t<2>;
// of complex numbers
using data_t = std::complex<double>;
// in file backed memory
using storage_t = pyre::memory::map_t<data_t>;
// to form a grid
using grid_t = pyre::grid::grid_t<packing_t, storage_t>;


// build a dataset
int
main(int argc, char * argv [])
{
    // initialize the journal
    pyre::journal::init(argc, argv);
    pyre::journal::application("qed");

    // generate {data}, a discretization of the domain (-2,2) x (-2,2) into square,
    // face centered pixels such that {data[0,0]} is at the origin

    // first, set up the discretization
    // pick a shape; based on my display resolution...
    grid_t::shape_type shape { 1964 * 2 + 1, 3024 * 2 + 1 };
    // center it
    grid_t::index_type origin = -shape / 2;
    // layout
    packing_t packing { shape, origin };
    // storage
    storage_t map("c16.dat", packing.cells());
    // grid
    grid_t data { packing, map };

    // the pixel width is determined by the largest extent
    auto delta = 4.0 / (shape.max() - 1);

    // here is the transform that converts an index into a complex number
    auto project = [delta](grid_t::index_type idx) -> data_t {
        // transform
        auto scaled = delta * idx;
        // convert into a {data_t}
        return data_t { scaled [0], scaled [1] };
    };

    // fill the grid
    for (auto idx : data.layout()) {
        // convert the indices into a complex number in our space
        auto z = project(idx);
        // compute f(z)
        auto f = (z - 1.0) / (z * z + z + 1.0);
        // place into the data set
        data [idx] = f;
    }

    // all done
    return 0;
}


// end of file
