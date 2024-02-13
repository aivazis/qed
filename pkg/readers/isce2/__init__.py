# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# publish the readers
from .Auto import Auto as auto
from .SLC import SLC as slc
from .interferogram import int
from .unwrapped import unw

# the metadata parser
from .xml import parse as metadata

# reader aliases
rslc = slc
gslc = slc


# end of file
