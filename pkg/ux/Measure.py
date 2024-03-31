# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import uuid


# the sync control
class Measure(
    qed.component, family="qed.ux.measure.measure", implements=qed.protocols.ux.measure
):
    """
    The measure layer options for a dataset
    """

    # user configurable state
    active = qed.properties.bool()
    active.default = False
    active.doc = "indicates whether the measure layer is active"

    path = qed.properties.list(schema=qed.properties.tuple(schema=qed.properties.int()))
    path.default = []
    path.doc = "the collection of points on the pixel path"

    closed = qed.properties.bool()
    closed.default = False
    closed.doc = "indicates whether the pixel path is closed"

    selection = qed.properties.list(schema=qed.properties.int())
    selection.default = []
    selection.doc = "the indices of the selected points"

    # support
    def clone(self):
        """
        Make a copy
        """
        # make a nae
        name = str(uuid.uuid1())
        # build a new instance and return it
        return type(self)(
            name=name,
            active=self.active,
            path=list(self.path),
            closed=self.closed,
            selection=list(self.selection),
        )


# end of file
