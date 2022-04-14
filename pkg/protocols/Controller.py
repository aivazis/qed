# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed
# my superclass
from .Producer import Producer


# the workflow
class Controller(Producer, family="qed.controller"):
    """
    Controllers help manage state that is manipulated interactively
    """


# end of file
