# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# helpers
from .Harvester import Harvester


# the dataset ux state
class Dataset(qed.component, family="qed.ux.datasets.dataset"):
    """
    The state of a dataset view
    """

    # configurable state
    measure = qed.protocols.ux.measure()
    measure.doc = "the measure layer indicator"

    sync = qed.protocols.ux.sync()
    sync.doc = "my sync table"

    zoom = qed.protocols.ux.zoom()
    zoom.doc = "the zoom level"

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)

        # remember my configuration so we can restore it on demand
        self.viewConfiguration = self.harvester.harvest(component=self)

        # all done
        return

    # singleton
    # the state harvester
    harvester = Harvester()


# end of file
