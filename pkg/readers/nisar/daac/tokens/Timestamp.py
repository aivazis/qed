# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Token import Token


# the timestamps in granule names
class Timestamp(Token, qed.properties.timestamp):
    """
    A timestamp in a granule name, in UTC; my subclasses say which clock it was read from and
    what it marks
    """

    # properties
    @property
    def lexer(self):
        """
        Generate my token recognizer
        """
        # form my recognizer
        return rf"(?P<{self.name}>\d{{8}}T\d{{6}})"

    # interface
    def gid(self, descriptor):
        """
        Render my value from {descriptor} in a format suitable for forming a granule id
        """
        # format the timestamp as YYYYMMDDTHHMMSS
        return getattr(descriptor, self.name).strftime(self.format)

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(default="20250731T123000", format="%Y%m%dT%H%M%S", **kwds)
        # all done
        return


# end of file
