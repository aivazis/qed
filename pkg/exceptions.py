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


# end of file
