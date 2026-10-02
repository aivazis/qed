# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# controllers
from .LinearRange import LinearRange as linearRange
from .LogRange import LogRange as logRange
from .Value import Value as value

# coupling the controllers of the channels that govern the same quantity
from .couple import couple

# end of file
