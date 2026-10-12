# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# get the base framework exception
from pyre import PyreError


# the base class for my exceptions
class QEDError(PyreError):
    """
    Base class for all qed errors
    """


# raised when a computation needs the extension and it is not there
class ExtensionError(QEDError):
    """
    Exception raised when the qed extension is needed and is not available

    The message is complete on its own, since it may travel back from a crew member as the
    reason a data product could not be staged
    """

    # public data
    description = "the qed extension is not available: {0.reason}"

    # metamethods
    def __init__(self, reason, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the reason
        self.reason = reason
        # all done
        return


# the base class for the edits of a pipeline diagram that cannot be made
class DiagramError(QEDError):
    """
    Base class for the edits of a pipeline diagram that cannot be made; an edit that raises one
    leaves the diagram and its recipe as they were
    """


# raised when a factory has no place for the slot of one of its traits
class UnplaceableSlotError(DiagramError):
    """
    Exception raised when a factory of a pipeline diagram has no spot for the slot of one of
    its traits
    """

    # public data
    description = "the factory '{0.factory}' has no place for the slot of its trait '{0.trait}'"

    # metamethods
    def __init__(self, factory, trait, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the name of the factory
        self.factory = factory
        # and the name of the trait
        self.trait = trait
        # all done
        return


# end of file
