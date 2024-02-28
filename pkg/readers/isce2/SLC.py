# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# access to the metadata parser
from . import xml

# superclass
from .. import native


# the SLC reader; SLCs contain one {complex64} dataset
class SLC(native.flat, family="qed.readers.isce2.slc"):
    """
    The reader of SLC files
    """

    # public data
    cell = qed.protocols.datatype()
    cell.default = "complex64"
    cell.doc = "the type of the dataset payload"

    # framework hooks
    def pyre_configured(self):
        """
        Hook invoked after the reader configuration is complete
        """
        # get the current value of my shape
        shape = list(self.shape) if self.shape else [0, 0]
        # if it's trivial
        if not shape or shape[0] == 0 or shape[1] == 0:
            # look for an auxiliary file with metadata and extract the available information
            metadata = xml.metadata(self.uri)
            # if it knows the number of lines
            if metadata.height:
                # set it
                shape[0] = metadata.height
            # if it knows the number of samples
            if metadata.width:
                # set it
                shape[1] = metadata.width
            # if the shape is now fully resolved
            if shape[0] and shape[1]:
                # set it
                self.shape = tuple(shape)
        # and chain up
        yield from super().pyre_configured()
        # all done
        return


# end of file
