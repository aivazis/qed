# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed


# the RSLC reader
class RSLC(qed.flow.factory, family="qed.isce2.readers.rslc", implements=qed.protocols.reader):
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

        # there is only one dataset in the file and it is structurally trivial
        dataset = qed.datasets.raw()

        # decorate it
        dataset.uri = self.uri
        dataset.shape = self.shape
        dataset.cell = qed.datatypes.complex64()
        dataset.tile = dataset.cell.tile
        # go through the default channels provided by the data type
        for channel in dataset.cell.channels:
            # and instantiate a workflow for each one
            dataset.channels[channel] = channel

        # finally, add it to the pile of datasets
        self.datasets.append(dataset)

        # all done
        return


# end of file
