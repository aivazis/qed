# -*- Makefile -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


# qed consists of a python package
qed.packages := qed.pkg
# libraries
qed.libraries := qed.lib
# python extensions
qed.extensions :=
# a ux bundle
qed.webpack := qed.ux
# and some tests
qed.tests := qed.pkg.tests


# load the packages
include $(qed.packages)
# the libraries
include $(qed.libraries)
# the extensions
include $(qed.extensions)
# the ux
include $(qed.webpack)
# and the test suites
include $(qed.tests)


# end of file
