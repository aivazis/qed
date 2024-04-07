# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
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


# end of file
