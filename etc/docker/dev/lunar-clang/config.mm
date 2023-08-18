# -*- Makefile -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 2022-2023 all rights reserved


# external dependencies
# system tools
sys.prefix := /usr
sys.lib := ${sys.prefix}/lib/${host.arch}-linux-gnu
# local installs
usr.prefix := /usr/local

# gsl
gsl.version := 2.7.1
gsl.dir := $(sys.prefix)

# hdf5
hdf5.version := 1.10.8
hdf5.dir := ${sys.prefix}
hdf5.parallel := serial
hdf5.incpath := $(hdf5.dir)/include/hdf5/$(hdf5.parallel)
hdf5.libpath := $(sys.lib)/hdf5/${hdf5.parallel}

# numpy
numpy.version := 1.24.2
numpy.dir := $(sys.prefix)/lib/python3/dist-packages/numpy/core

# pybind11
pybind11.version := 2.10.3
pybind11.dir = $(sys.prefix)

# python
python.version := @PYTHON_VERSION@
python.dir := $(sys.prefix)

# pyre
pyre.version := 1.12.1
pyre.dir := $(usr.prefix)

# install locations
# this is necessary in order to override {mm} appending the build type to the install prefix
builder.dest.prefix := $(project.prefix)/
# install the python packages straight where they need to go
builder.dest.pyc := $(sys.prefix)/lib/python3/dist-packages/

# control over the build process
# set the python compiler so we don't depend on the symbolic link, which may not even be there
python3.driver := python$(python.version)


# end of file
