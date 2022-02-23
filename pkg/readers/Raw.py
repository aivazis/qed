# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed


# the Raw reader
class Raw(qed.flow.factory, family="qed.readers.raw", implements=qed.protocols.reader):
    """
    The reader for raw files
    """


    # public data
    uri = qed.properties.path()
    uri.doc = "the uri of the data source"

    cell = qed.protocols.datatype()
    cell.default = None
    cell.doc = "the type of the dataset payload"

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
        dataset = qed.datasets.raw(name=f"{self.pyre_name}.data")

        # decorate it
        dataset.uri = self.uri
        dataset.shape = self.shape
        dataset.cell = self.cell
        dataset.tile = self.cell.tile
        # go through the default channels provided by the data type
        for channel in self.cell.channels:
            # get their factories
            cls = qed.protocols.channel.pyre_resolveSpecification(channel)
            # and instantiate a workflow for each one
            dataset.channels[channel] = cls(name=f"{dataset.pyre_name}.{channel}")

        # finally, add it to the pile of datasets
        self.datasets.append(dataset)

        # all done
        return


# end of file
