# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# datasets
# memory mapped files from the local filesystem
from .MemoryMap import MemoryMap as mmap

# lines laid out in the records of a file, e.g. the image file of a CEOS product
from .Records import Records as records

# carefully
try:
    # load the support for {gdal} rasters
    from .GDALBand import GDALBand as gdal
# if it fails
except ImportError:
    # no worries
    pass


# end of file
