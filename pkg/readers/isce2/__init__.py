# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# the metadata parser
from .xml import metadata, parse

# publish the readers
from .Auto import Auto as auto
from .SLC import SLC as slc
from .interferogram import int
from .unwrapped import unw

# reader aliases
rslc = slc
gslc = slc


# end of file
