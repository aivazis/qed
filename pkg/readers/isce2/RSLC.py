# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed


# the RSLC reader
class RSLC(qed.flow.factory, family="qed.readers.isce2.rslc", implements=qed.protocols.reader):
    """
    The reader of RSLC files
    """


    # public data
    uri = qed.properties.path()
    uri.doc = "the uri of the data source"

    shape = qed.properties.tuple(schema=qed.properties.int())
    shape.doc = "the size of the dataset in (lines, samples)"

    selectors = qed.protocols.selectors()
    selectors.default = {}
    selectors.doc = "a map of selector names to their allowed values"

    datasets = qed.properties.list(schema=qed.protocols.dataset.output())
    datasets.doc = "the list of data sets provided by the reader"


    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)

        # there is only one dataset in the file
        dataset = qed.datasets.raw()
        # decorate it
        dataset.shape = self.shape
        dataset.cell = qed.datatypes.complex4()
        dataset.tile = dataset.cell.tile
        # and attach it
        self.datasets.append(dataset)

        # all done
        return


# end of file
