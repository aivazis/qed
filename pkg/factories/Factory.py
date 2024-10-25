# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# framework
import qed


# base class for local factories
class Factory(
    qed.flow.factory, implements=qed.protocols.factories.producer, internal=True
):
    """
    The base class for {qed} factories
    """


# end of file
