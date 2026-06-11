# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal
import uuid


# the look-at control
class Center(
    qed.component, family="qed.ux.center.center", implements=qed.protocols.ux.center
):
    """
    The source pixel that sits at the center of the viewport
    """

    # user configurable state
    row = qed.properties.float()
    row.default = 0
    row.doc = "the source row under the viewport center"

    col = qed.properties.float()
    col.default = 0
    col.doc = "the source column under the viewport center"

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
            row=self.row,
            col=self.col,
        )

    def reset(self, defaults):
        """
        Reset my state
        """
        # reset my state
        self.row = defaults.row
        self.col = defaults.col
        # mark me as clean
        self.dirty = False
        # all done
        return self

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # initially, i'm clean
        self.dirty = False
        # all done
        return

    # framework hooks
    def pyre_traitModified(self, **kwds):
        """
        Hook that gets invoked by the framework right after a trait value has been modified.
        """
        # chain up
        super().pyre_traitModified(**kwds)
        # mark me as dirty
        self.dirty = True
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
        channel.line(f"center: {self}")
        # my contents
        channel.indent()
        channel.line(f"row: {self.row}")
        channel.line(f"col: {self.col}")
        channel.outdent()
        # flush
        channel.log()
        # all done
        return


# end of file
