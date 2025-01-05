# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# generic channels
from .Amplitude import Amplitude as amplitude
from .Complex import Complex as complex
from .Phase import Phase as phase


# build the list of supported channels
def channels():
    """
    Generate a sequence of unwrapped channels
    """
    # complex
    yield complex
    # amplitude
    yield amplitude
    # phase
    yield phase

    # all done
    return


# end of file
