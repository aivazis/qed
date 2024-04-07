# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal
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
    def clone(self, name=None):
        """
        Make a copy
        """
        # make a name, if necessary
        name = str(uuid.uuid1()) if name is None else name
        # build a new instance and return it
        return type(self)(
            name=name,
            active=self.active,
            path=list(self.path),
            closed=self.closed,
            selection=list(self.selection),
        )

    def reset(self, defaults):
        """
        Reset my state to its {defaults}
        """
        # reset
        self.active = defaults.active
        self.path = list(defaults.path)
        self.closed = defaults.closed
        self.selection = list(defaults.selection)
        # all done
        return self

    # debugging support
    def pyre_dump(self):
        """
        Render my state
        """
        # make a channel
        channel = journal.info("qed.ux.measure")
        # sign in
        channel.line(f"measure: {self}")
        # my contents
        channel.indent()
        channel.line(f"active: {self.active}")

        path = self.path
        if path:
            channel.line(f"path: [")
            channel.indent()
            for point in self.path:
                channel.line(f"{point}")
            channel.line(f"]")
            channel.outdent()
        # otherwise
        else:
            channel.line(f"path: []")

        channel.line(f"selection: {self.selection}")
        channel.line(f"closed: {self.closed}")
        channel.outdent()
        # flush
        channel.log()
        # all done
        return


# end of file
