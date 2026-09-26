# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved

# the base reader support
from . import native

# specialized readers
from . import isce2
from . import alos
from . import nisar
from . import asar

# reader metadata
from .Metadata import Metadata as metadata

# the statistics prober the dataset flavors seed themselves with
from .probes import probe, windows

# how the chunks of a dataset sit on the pages of its file
from . import pages

# end of file
