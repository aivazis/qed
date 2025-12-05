# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed


# a stack of readers
class Stack(
    qed.flow.factory, family="qed.readers.stacks.stack", implements=qed.protocols.stack
):
    """
    A stack of readers
    """

    # my readers
    readers = qed.properties.list(schema=qed.protocols.reader())
    readers.doc = "the readers of my stack"


# end of file
