# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed

# my superclass
from .Producer import Producer

# my readers
from .Reader import Reader


# the product payload
class Stack(Producer, family="qed.stacks"):
    """
    A dataset factory
    """

    # public data
    readers = qed.properties.list(schema=Reader())
    readers.doc = "the list of readers that form the stack"


# end of file
