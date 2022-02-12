// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// wrappers over {pyre::memory::map} template expansions
// build the submodule
void
qed::py::channels::channels(py::module & m)
{
    // create a {channels} submodule
    auto channels = m.def_submodule(
        // the name of the module
        "channels",
        // its docstring
        "support for predefined {channels}");

    // add the supported channels
    amplitude(channels);
    complex(channels);
    imaginary(channels);
    phase(channels);
    real(channels);

    // all done
    return;
}


// amplitude
void
qed::py::channels::amplitude(py::module & m)
{
    // type aliases
    using floats_t = source_t<std::complex<float>>;
    using floats_const_reference = const floats_t &;


    m.def(
        // the name of the function
        "amplitudeComplexFloat",
        // the handler
        [](floats_const_reference source, int zoom, floats_t::index_type origin,
           floats_t::shape_type shape, double min, double max) -> bmp_t {
            // my decimator
            using zoom_t = pyre::viz::filters::decimate_t<floats_t>;
            // a filter over a grid iterator
            using amplitude_t = pyre::viz::filters::amplitude_t<zoom_t>;
            // my normalizer
            using norm_t = pyre::viz::filters::parametric_t<amplitude_t>;
            // a gray color map over the amplitude
            using graymap_t = pyre::viz::colormaps::gray_t<norm_t>;

            // make a bitmap
            bmp_t bmp(shape[0], shape[1]);

            // the decimator
            auto decimator = zoom_t(source, origin, shape, 1 << zoom);
            // make an amplitude filter and wire it to the tile
            auto filter = amplitude_t(decimator);
            // the normalizer
            auto norm = norm_t(filter, norm_t::interval_type(min, max));
            // make a color map
            graymap_t colormap(norm);
            // encode
            bmp.encode(colormap);

            // and return it
            return bmp;
        },
        // the signature
        "source"_a, "zoom"_a, "origin"_a, "shape"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex float tile");


    // all done
    return;
}


// complex
void
qed::py::channels::complex(py::module & m)
{
    // all done
    return;
}


// imaginary
void
qed::py::channels::imaginary(py::module & m)
{
    // all done
    return;
}


// phase
void
qed::py::channels::phase(py::module & m)
{
    // all done
    return;
}


// real
void
qed::py::channels::real(py::module & m)
{
    // all done
    return;
}


// end of file
