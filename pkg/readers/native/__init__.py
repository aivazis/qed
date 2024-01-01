# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
from qed import foundry

# publish
from . import channels
from . import datasets

# readers
from .Flat import Flat as flat


# make one
@foundry(tip="a reader for all formats supported by GDAL")
def gdal():
    # carefully
    try:
        # load the reader
        from .GDAL import GDAL
    # if anything goes wring
    except ImportError:
        # bail
        return
    # otherwise, steal its docstring
    __doc__ = GDAL.__doc__
    # and return it
    return GDAL


# end of file
