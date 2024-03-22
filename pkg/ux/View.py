# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed


# information about the contents of a view
class View(
    qed.component, family="qed.views.view", implements=qed.protocols.view
):
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


# end of file
