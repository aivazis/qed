# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# superclass
from .Node import Node


# representation of textual data on the diagram
class Label(Node):
    """
    Representation of text at a specific location in the diagram
    """

    # the entity i belong to, once it claims me
    owner = None

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
    def __init__(
        self, category, delta, position, given=None, family=None, role=None, traits=(), **kwds
    ):
        # apply the delta
        shifted = (p + dp for p, dp in zip(position, delta))
        # chain up
        super().__init__(position=shifted, **kwds)
        # the parts of what i say, each one left out when it does not apply, so whoever draws me
        # decides how to put them together: the given name of an instance, possibly empty when
        # nobody gave it one, and none for anything that is not an instance
        self.given = given
        # the family of the component it is, if it is one
        self.family = family
        # the role of the protocol it satisfies, if it is known
        self.role = role
        # and the names of the traits of a connector
        self.traits = list(traits)
        # save the category
        self.category = category
        # and the relative position
        self.delta = delta
        # all done
        return


# end of file
