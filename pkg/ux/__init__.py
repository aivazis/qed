# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# the dispatcher
def dispatcher(**kwds):
    """
    The handler of {uri} requests
    """
    # get the dispatcher
    from .Dispatcher import Dispatcher
    # instantiate and return
    return Dispatcher(**kwds)


# the app engine
def panel(**kwds):
    """
    The application engine
    """
    # get the factory
    from .Panel import Panel
    # instantiate and return
    return Panel(**kwds)


# end of file
