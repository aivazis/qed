# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal
import uuid


# the sync control
class Sync(qed.component, family="qed.ux.sync.sync", implements=qed.protocols.ux.sync):
    """
    The sync options for a dataset
    """

    # user configurable state
    channel = qed.properties.bool()
    channel.default = False
    channel.doc = "the channel sync flag"

    zoom = qed.properties.bool()
    zoom.default = False
    zoom.doc = "the zoom sync flag"

    scroll = qed.properties.bool()
    scroll.default = False
    scroll.doc = "the scroll sync flag"

    path = qed.properties.bool()
    path.default = False
    path.doc = "the path sync flag"

    offsets = qed.properties.tuple(schema=qed.properties.int())
    offsets.default = (0, 0)
    offsets.doc = (
        "relative offset to apply to this viewport when synchronized scrolling"
    )

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
            channel=self.channel,
            zoom=self.zoom,
            scroll=self.scroll,
            path=self.path,
            offsets=tuple(self.offsets),
        )

    def reset(self, defaults):
        """
        Reset my state to its {defaults}
        """
        # reset
        self.channel = defaults.channel
        self.zoom = defaults.zoom
        self.scroll = defaults.scroll
        self.path = defaults.path
        self.offsets = defaults.offsets
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
        channel.line(f"sync: {self}")
        # my contents
        channel.indent()
        channel.line(f"channel: {self.channel}")
        channel.line(f"path: {self.path}")
        channel.line(f"scroll: {self.scroll}")
        channel.line(f"zoom: {self.zoom}")
        channel.line(f"offsets: {self.offsets}")
        channel.outdent()
        # flush
        channel.log()
        # all done
        return


# end of file
