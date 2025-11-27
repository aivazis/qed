# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed

# publish
from . import channels
from . import datasets

# readers
from .Flat import Flat as flat


# make one
@qed.foundry(tip="a reader for all formats supported by GDAL")
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


# metadata factory
def metadata(uri, **kwds):
    """
    Build a metadata object
    """
    # instantiate the object
    metadata = qed.readers.metadata()
    # attach the uri
    metadata.uri = uri
    # if the product is local
    if metadata.uri.scheme == "file":
        # form the path
        path = qed.primitives.path(metadata.uri.address)
        # grab the file size and add it to the pile
        metadata.bytes = path.stat().st_size
    # that's all we know, for now
    return metadata


# end of file
