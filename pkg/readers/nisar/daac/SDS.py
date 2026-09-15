# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .NISAR import NISAR

# tokens
from . import tokens


# the base descriptor for all NISAR products
class SDS(NISAR, internal=True):
    """
    The RRST product descriptor
    """

    # constants
    stage = "unknown"

    # tokens
    band = tokens.band()
    level = tokens.level(default=0)
    # CRID
    environment = tokens.environment()
    phase = tokens.phase()
    major = tokens.major()
    minor = tokens.minor()
    patch = tokens.patch()
    # others
    sds = tokens.sds()
    counter = tokens.counter()

    # interface
    @property
    def instrument(self):
        """
        Return the instrument name
        """
        # this doubles as the way to discover the name of the top level group in the h5 file
        return f"{self.band}SAR"

    @property
    def filename(self):
        """
        Build the canonical filename for this product
        """
        # easy
        return qed.primitives.path(f"{self.gid}{self.extension}")

    # metamethods
    def __init__(self, name, granule, **kwds):
        # the granule id is the stem; drop any extension that came along with it
        granule, *_ = granule.split(".")
        # chain up
        super().__init__(name=name, granule=granule, **kwds)
        # all done
        return

    # implementation details
    @classmethod
    def sequencer(cls):
        """
        Generate the sequence of token names as they appear in valid granule ids of my type
        """
        # whatever my superclass has
        yield from super().sequencer()
        # plus the common prefix
        yield from [
            # the instrument band
            "band",
            # the product level
            "level",
            # a separator
            "separator",
        ]
        # all done
        return

    # constants
    extension = ".h5"


# end of file
