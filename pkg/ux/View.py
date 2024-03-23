# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal


# information about the contents of a view
class View(qed.component, family="qed.views.view", implements=qed.protocols.view):
    """
    Detailed information about the contents of a mounted view
    """

    # state
    reader = qed.protocols.reader()
    reader.doc = "the reader whose dataset is being displayed"

    dataset = qed.protocols.dataset()
    dataset.doc = "the displayed dataset"

    channel = qed.protocols.channel()
    channel.doc = "the displayed channel"

    selections = qed.properties.kv()
    selections.default = {}
    selections.doc = "a key/value map with the user selections"

    def pyre_dump(self):
        """
        Report my state
        """
        # make a channel
        channel = journal.info("qed.ux.store")
        # sign in
        channel.line(f"{self}")
        # report
        channel.indent()
        channel.line(f"reader: {self.reader}")
        channel.line(f"dataset: {self.dataset}")
        channel.line(f"channel: {self.channel}")
        channel.line(f"selections:")
        channel.indent()
        for key, value in self.selections:
            channel.line(f"{key}: {value}")
        channel.outdent()
        channel.outdent()
        # flush
        channel.log()
        # all done
        return


# end of file
