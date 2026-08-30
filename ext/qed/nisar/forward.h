// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#if !defined(qed_py_nisar_forward_h)
#define qed_py_nisar_forward_h


// set up the namespace
namespace qed::py::nisar {
    // the module linitializers
    // top level
    void nisar(py::module &);

    // data products
    void real(py::module &);
    void slc(py::module &);
    void stack(py::module &);
    void bfpq(py::module &);
    void masks(py::module &);
    // profile
    void profile(py::module &);
    // the statistics of the encoded products, whose decoders make their own cells
    void stats(py::module &);

    // the kernels that read a raster of a given cell type
    void cells(py::module &);
}


#endif

// end of file
