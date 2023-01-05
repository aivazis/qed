# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# support
import qed
# my superclass
from .Producer import Producer


# the workflow
class Channel(Producer, family="qed.channels"):
    """
    A channel is a visualization workflow
    """


# end of file
