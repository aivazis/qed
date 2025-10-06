# -*- Makefile -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# external dependencies
# system tools
sys.prefix := ${CONDA_PREFIX}

# cspice
cspice.version := 7.0.0
cspice.dir := $(sys.prefix)

# gsl
gsl.version := 2.7.1
gsl.dir := $(sys.prefix)

# hdf5
hdf5.version := 1.14.5
hdf5.dir := ${sys.prefix}
hdf5.parallel := off

# libpq
libpq.version := 17.2
libpq.dir := ${sys.prefix}

# proj
proj.version := 9.6.0
proj.dir := $(sys.prefix)

# python
python.version := @PYTHON_VERSION@
python.dir := $(sys.prefix)

# numpy
numpy.version := 2.1.3
numpy.dir := $(sys.prefix)/lib/python3/dist-packages/numpy/_core

# pybind11
pybind11.version := 2.11.1
pybind11.dir = $(sys.prefix)

# pyre
pyre.version := 1.12.5
pyre.dir := $(sys.prefix)

# install locations
# this is necessary in order to override {mm} appending the build type to the install prefix
builder.dest.prefix := $(project.prefix)/
# install the python packages straight where they need to go
builder.dest.pyc := $(sys.prefix)/lib/python3/dist-packages/

# control over the build process
# set the python compiler so we don't depend on the symbolic link, which may not even be there
python3.driver := python$(python.version)


# end of file
