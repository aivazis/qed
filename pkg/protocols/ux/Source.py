# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed

# my parts
from .Measure import Measure
from .Sync import Sync
from .Zoom import Zoom


# the dataset ux state
class Source(qed.protocol, family="qed.ux.sources"):
    """
    The state of a dataset view
    """

    # configurable state
    measure = Measure()
    measure.doc = "the measure layer indicator"

    sync = Sync()
    sync.doc = "my sync table"

    zoom = Zoom()
    zoom.doc = "the zoom level"

    # framework hooks
    @classmethod
    def pyre_default(cls, **kwds):
        """
        Pick a default implementation
        """
        # use the dataset base
        return qed.ux.source


# end of file
