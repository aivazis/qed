# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# the app engine
def panel(**kwds):
    """
    The application engine
    """
    # get the factory
    from .Panel import Panel

    # instantiate and return
    return Panel(**kwds)


# the dispatcher
from .Dispatcher import Dispatcher as dispatcher

# the application store
from .Store import Store as store

# channel view state
from .Channel import Channel as channel

# controls
from .Measure import Measure as measure
from .Sync import Sync as sync
from .Zoom import Zoom as zoom

# end of file
