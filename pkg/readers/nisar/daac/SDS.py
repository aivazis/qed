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

    # tokens: the radar band
    band = tokens.band()
    # the processing level
    level = tokens.level(default=0)
    # the composite release identifier, EMMmmp: the environment
    environment = tokens.environment()
    # the major release
    major = tokens.major()
    # the minor release
    minor = tokens.minor()
    # and the patch
    patch = tokens.patch()
    # the location of the science data system that made the product
    sds = tokens.sds()
    # and the product counter
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
    def venue(self):
        """
        The meaning of my environment letter, or "user extension" for a letter the naming
        conventions do not define
        """
        # my environment token knows
        return self.pyre_trait(alias="environment").describe(self.environment)

    @property
    def filename(self):
        """
        Build the canonical filename for this product
        """
        # easy
        return qed.primitives.path(f"{self.gid}{self.extension}")

    # metamethods
    def __init__(self, name, granule, **kwds):
        # {qed} strips all extensions from the SDS granule ids
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
