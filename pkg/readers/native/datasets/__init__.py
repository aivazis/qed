# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# datasets
# memory mapped files from the local filesystem
from .MemoryMap import MemoryMap as mmap

# carefully
try:
    # load the support for {gdal} rasters
    from .GDALBand import GDALBand as gdal
# if it fails
except ImportError:
    # no worries
    pass


# end of file
