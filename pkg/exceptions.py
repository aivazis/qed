# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# get the base framework exception
from pyre import PyreError


# the base class for my exceptions
class QEDError(PyreError):
    """
    Base class for all qed errors
    """


# component configuration errors
class ConfigurationError(QEDError):
    """
    Exception raised when qed components detect inconsistencies in their configurations
    """

    # public data
    description = "configuration error: {0.reason}"

    # meta-methods
    def __init__(self, reason, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the error info
        self.reason = reason
        # all done
        return


# end of file
