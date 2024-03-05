# -*- Makefile -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# external dependencies
# system tools
sys.prefix := ${CONDA_PREFIX}

# gsl
gsl.version := 2.7
gsl.dir := $(sys.prefix)

# hdf5
hdf5.version := 1.15.0
hdf5.dir := ${sys.prefix}
hdf5.parallel := off

# libpq
libpq.version := 16.1
libpq.dir := ${sys.prefix}

# pybind11
pybind11.version := 2.11.1
pybind11.dir = $(sys.prefix)

# python
python.version := @PYTHON_VERSION@
python.dir := $(sys.prefix)

# numpy
numpy.version := 1.26.3
numpy.dir := $(sys.prefix)/lib/python$(python.version)/site-packages/numpy/core

# pyre
pyre.version := 1.12.4
pyre.dir := $(sys.prefix)

# install the python packages straight where they need to go
builder.dest.pyc := $(sys.prefix)/lib/python$(python.version)/site-packages/

# control over the build process
# set the python compiler so we don't depend on the symbolic link, which may not even be there
python3.driver := python$(python.version)


# end of file
