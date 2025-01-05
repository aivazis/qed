// -*- c++ -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
#include "external.h"
// namespace setup
#include "forward.h"


// submodule with the bindings for the native tile generators
void
qed::py::native::channels(py::module & m)
{
    // create a {channels} submodule
    auto channels = m.def_submodule(
        // the name of the module
        "channels",
        // its docstring
        "support for native {channels}");


    // add the individual channel bindings
    // {b} value
    channels.def(
        // the name of the function
        "value",
        // the handler
        &qed::native::channels::value<mapgrid_t<char>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the value of a byte tile");
    // {i2} value
    channels.def(
        // the name of the function
        "value",
        // the handler
        &qed::native::channels::value<mapgrid_t<int16_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the value of a int16_t tile");
    // {i4} value
    channels.def(
        // the name of the function
        "value",
        // the handler
        &qed::native::channels::value<mapgrid_t<int32_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the value of an int32_t tile");
    // {i8} value
    channels.def(
        // the name of the function
        "value",
        // the handler
        &qed::native::channels::value<mapgrid_t<int64_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the value of a int64_t tile");
    // {r4} value
    channels.def(
        // the name of the function
        "value",
        // the handler
        &qed::native::channels::value<mapgrid_t<float>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the value of a float tile");
    // {r8} value
    channels.def(
        // the name of the function
        "value",
        // the handler
        &qed::native::channels::value<mapgrid_t<double>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the value of a double tile");

    // add the individual channel bindings for views
    // {b} value
    channels.def(
        // the name of the function
        "value",
        // the handler
        &qed::native::channels::value<viewgrid_t<char>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the value of a byte tile");
    // {i2} value
    channels.def(
        // the name of the function
        "value",
        // the handler
        &qed::native::channels::value<viewgrid_t<int16_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the value of a int16_t tile");
    // {i4} value
    channels.def(
        // the name of the function
        "value",
        // the handler
        &qed::native::channels::value<viewgrid_t<int32_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the value of an int32_t tile");
    // {i8} value
    channels.def(
        // the name of the function
        "value",
        // the handler
        &qed::native::channels::value<viewgrid_t<int64_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the value of a int64_t tile");
    // {r4} value
    channels.def(
        // the name of the function
        "value",
        // the handler
        &qed::native::channels::value<viewgrid_t<float>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the value of a float tile");
    // {r8} value
    channels.def(
        // the name of the function
        "value",
        // the handler
        &qed::native::channels::value<viewgrid_t<double>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the value of a double tile");

    // {b} abs
    channels.def(
        // the name of the function
        "abs",
        // the handler
        &qed::native::channels::magnitude<mapgrid_t<char>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of a byte tile");
    // {i2} abs
    channels.def(
        // the name of the function
        "abs",
        // the handler
        &qed::native::channels::magnitude<mapgrid_t<int16_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of a int16_t tile");
    // {i4} abs
    channels.def(
        // the name of the function
        "abs",
        // the handler
        &qed::native::channels::magnitude<mapgrid_t<int32_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of an int32_t tile");
    // {i8} abs
    channels.def(
        // the name of the function
        "abs",
        // the handler
        &qed::native::channels::magnitude<mapgrid_t<int64_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of a int64_t tile");
    // {r4} abs
    channels.def(
        // the name of the function
        "abs",
        // the handler
        &qed::native::channels::magnitude<mapgrid_t<float>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of a float tile");
    // {r8} abs
    channels.def(
        // the name of the function
        "abs",
        // the handler
        &qed::native::channels::magnitude<mapgrid_t<double>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of a double tile");

    // {b} abs
    channels.def(
        // the name of the function
        "abs",
        // the handler
        &qed::native::channels::magnitude<viewgrid_t<char>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of a byte tile");
    // {i2} abs
    channels.def(
        // the name of the function
        "abs",
        // the handler
        &qed::native::channels::magnitude<viewgrid_t<int16_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of a int16_t tile");
    // {i4} abs
    channels.def(
        // the name of the function
        "abs",
        // the handler
        &qed::native::channels::magnitude<viewgrid_t<int32_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of an int32_t tile");
    // {i8} abs
    channels.def(
        // the name of the function
        "abs",
        // the handler
        &qed::native::channels::magnitude<viewgrid_t<int64_t>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of a int64_t tile");
    // {r4} abs
    channels.def(
        // the name of the function
        "abs",
        // the handler
        &qed::native::channels::magnitude<viewgrid_t<float>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of a float tile");
    // {r8} abs
    channels.def(
        // the name of the function
        "abs",
        // the handler
        &qed::native::channels::magnitude<viewgrid_t<double>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the absolute value of a double tile");

    channels.def(
        // the name
        "value",
        // the handler
        [](py::array_t<float, py::array::c_style | py::array::forcecast> source, shape2d_t shape,
           float low, float high) {
            // type aliases
            // the normalizer
            using norm_t = parametric_t<const float *>;
            // the color map
            using colormap_t = gray_t<norm_t>;
            // get the array data buffer
            auto buffer = static_cast<const float *>(source.request().ptr);
            // map to the unit interval
            auto norm = norm_t(buffer, norm_t::interval_type(low, high));
            // generate color
            auto colormap = colormap_t(norm);

            // make a bitmap
            bmp_t bmp(shape[0], shape[1]);
            // render
            bmp.encode(colormap);
            // and return it
            return bmp;
        },
        // the signature
        "source"_a, "shape"_a, "low"_a, "high"_a,
        // the docstring
        "render the values of a numpy array");

    // {c8} amplitude
    channels.def(
        // the name of the function
        "amplitude",
        // the handler
        &qed::native::channels::amplitude<mapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex float tile");
    // {c16} amplitude
    channels.def(
        // the name of the function
        "amplitude",
        // the handler
        &qed::native::channels::amplitude<mapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex double tile");

    // {c8}
    channels.def(
        // the name of the function
        "complex",
        // the handler
        &qed::native::channels::complex<mapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a, "minPhase"_a, "maxPhase"_a,
        "saturation"_a,
        // the docstring
        "render the value of a complex float tile");
    // {c16}
    channels.def(
        // the name of the function
        "complex",
        // the handler
        &qed::native::channels::complex<mapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a, "minPhase"_a, "maxPhase"_a,
        "saturation"_a,
        // the docstring
        "render the value of a complex double tile");

    // imaginary part of {c8}
    channels.def(
        // the name of the function
        "imaginary",
        // the handler
        &qed::native::channels::imaginary<mapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the imaginary part a complex float tile");
    // imaginary part of {c16}
    channels.def(
        // the name of the function
        "imaginary",
        // the handler
        &qed::native::channels::imaginary<mapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the imaginary part of a complex double tile");

    // phase of {c8}
    channels.def(
        // the name of the function
        "phase",
        // the handler
        &qed::native::channels::phase<mapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "low"_a, "high"_a, "saturation"_a,
        "brightness"_a,
        // the docstring
        "render the phase of a complex float tile");
    // phase of {c16}
    channels.def(
        // the name of the function
        "phase",
        // the handler
        &qed::native::channels::phase<mapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "low"_a, "high"_a, "saturation"_a,
        "brightness"_a,
        // the docstring
        "render the phase of a complex double tile");

    // real part of {c8}
    channels.def(
        // the name of the function
        "real",
        // the handler
        &qed::native::channels::real<mapgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the real part a complex float tile");
    // real part of {c16}
    channels.def(
        // the name of the function
        "real",
        // the handler
        &qed::native::channels::real<mapgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the real part of a complex double tile");

    // {c8} amplitude
    channels.def(
        // the name of the function
        "amplitude",
        // the handler
        &qed::native::channels::amplitude<viewgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex float tile");
    // {c16} amplitude
    channels.def(
        // the name of the function
        "amplitude",
        // the handler
        &qed::native::channels::amplitude<viewgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the amplitude of a complex double tile");

    // {c8}
    channels.def(
        // the name of the function
        "complex",
        // the handler
        &qed::native::channels::complex<viewgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a, "minPhase"_a, "maxPhase"_a,
        "saturation"_a,
        // the docstring
        "render the value of a complex float tile");
    // {c16}
    channels.def(
        // the name of the function
        "complex",
        // the handler
        &qed::native::channels::complex<viewgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a, "minPhase"_a, "maxPhase"_a,
        "saturation"_a,
        // the docstring
        "render the value of a complex double tile");

    // imaginary part of {c8}
    channels.def(
        // the name of the function
        "imaginary",
        // the handler
        &qed::native::channels::imaginary<viewgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the imaginary part a complex float tile");
    // imaginary part of {c16}
    channels.def(
        // the name of the function
        "imaginary",
        // the handler
        &qed::native::channels::imaginary<viewgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the imaginary part of a complex double tile");

    // phase of {c8}
    channels.def(
        // the name of the function
        "phase",
        // the handler
        &qed::native::channels::phase<viewgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "low"_a, "high"_a, "saturation"_a,
        "brightness"_a,
        // the docstring
        "render the phase of a complex float tile");
    // phase of {c16}
    channels.def(
        // the name of the function
        "phase",
        // the handler
        &qed::native::channels::phase<viewgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "low"_a, "high"_a, "saturation"_a,
        "brightness"_a,
        // the docstring
        "render the phase of a complex double tile");

    // real part of {c8}
    channels.def(
        // the name of the function
        "real",
        // the handler
        &qed::native::channels::real<viewgrid_t<std::complex<float>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the real part a complex float tile");
    // real part of {c16}
    channels.def(
        // the name of the function
        "real",
        // the handler
        &qed::native::channels::real<viewgrid_t<std::complex<double>>>,
        // the signature
        "source"_a, "origin"_a, "shape"_a, "stride"_a, "min"_a, "max"_a,
        // the docstring
        "render the real part of a complex double tile");

    // all done
    return;
}


// end of file
