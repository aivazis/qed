# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# generic channels
from .Amplitude import Amplitude as amplitude
from .Complex import Complex as complex
from .Imaginary import Imaginary as imaginary
from .Phase import Phase as phase
from .Real import Real as real


# build the list of supported channels
def channels():
    """
    Generate a sequence of interferogram channels
    """
    # complex
    yield complex
    # amplitude
    yield amplitude
    # phase
    yield phase
    # real part
    yield real
    # imaginary part
    yield imaginary

    # all done
    return


# end of file
