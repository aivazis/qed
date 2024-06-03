# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal
import uuid


# the sync control
class Flow(qed.component, family="qed.ux.flow.flow", implements=qed.protocols.ux.flow):
    """
    The flow layer options for a dataset
    """

    # user configurable state
    active = qed.properties.bool()
    active.default = False
    active.doc = "indicates whether the flow layer is active"

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
        )

    def reset(self, defaults):
        """
        Reset my state to its {defaults}
        """
        # reset
        self.active = defaults.active
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
        channel = journal.info("qed.ux.flow")
        # sign in
        channel.line(f"flow: {self}")
        # my contents
        channel.indent()
        channel.line(f"active: {self.active}")
        channel.outdent()
        # flush
        channel.log()
        # all done
        return


# end of file
