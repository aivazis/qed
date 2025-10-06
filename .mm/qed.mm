# -*- Makefile -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# qed consists of a python package
qed.packages := qed.pkg
# libraries
qed.libraries := qed.lib
# python extensions
qed.extensions := qed.ext
# a ux bundle
qed.webpack := qed.ux
# tests
qed.tests := qed.pkg.tests qed.ext.tests qed.data
# docker images
qed.docker-images := \
    qed.ci.lunar-gcc qed.ci.jammy-gcc  \
    qed.dev.native.jammy-clang qed.dev.native.jammy-gcc  \
    qed.dev.native.lunar-clang qed.dev.native.lunar-gcc  \
    qed.dev.native.mantic-clang qed.dev.native.mantic-gcc  \
    qed.dev.micromamba.noble-clang qed.dev.micromamba.noble-gcc  \
    qed.dev.micromamba.plucky-clang qed.dev.micromamba.plucky-gcc  \

# load the packages
include $(qed.packages)
# the libraries
include $(qed.libraries)
# the extensions
include $(qed.extensions)
# the ux
include $(qed.webpack)
# the test suites
include $(qed.tests)
# and the docker images
include $(qed.docker-images)


# end of file
