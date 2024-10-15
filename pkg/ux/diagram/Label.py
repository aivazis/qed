# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# superclass
from .Node import Node


# representation of textual data on the diagram
class Label(Node):
    """
    Representation of text at a specific location in the diagram
    """

    # interface
    def move(self, position):
        """
        Move to the new {position} shifted by my {delta}
        """
        # recompute my position
        shift = (p + dp for p, dp in zip(position, self.delta))
        # and make the move
        return super().move(position=shift)

    # metamethods
    def __init__(self, text, category, delta, position, **kwds):
        # apply the delta
        shifted = (p + dp for p, dp in zip(position, delta))
        # chain up
        super().__init__(position=shifted, **kwds)
        # save the text; expected to be a list of strings
        self.text = text
        # save the category
        self.category = category
        # and the relative position
        self.delta = delta
        # all done
        return


# end of file
