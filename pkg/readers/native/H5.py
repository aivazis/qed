# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed


# the basic reader for products in HDF5 format
class H5(qed.flow.factory, family="qed.readers.h5", implements=qed.protocols.reader):
    """
    The reader of HDF5 files
    """


    # public data
    uri = qed.properties.path()
    uri.doc = "the uri of the data source"

    datasets = qed.properties.list(schema=qed.protocols.dataset.output())
    datasets.doc = "the list of data sets provided by the reader"

    selectors = qed.protocols.selectors()
    selectors.doc = "a map of selector names to their allowed values"


    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)

        # open my file
        self.h5 = qed.libh5.File(path=str(self.uri))

        # all done
        return



# end of file
