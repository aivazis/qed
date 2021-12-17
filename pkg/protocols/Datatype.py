# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2021 all rights reserved


# support
import qed
# my superclass
from .Specification import Specification


# the dataset layout
class Datatype(Specification, family="qed.datatypes"):
    """
    The datatype metadats
    """


    # public data
    # individual metadata, used to assemble a default layout
    cell = qed.properties.str()
    cell.doc = "the format string that specifies the type of the dataset payload"

    channels = qed.properties.strings()
    channels.doc = "the names of the channels provided by this datatype"


# end of file
