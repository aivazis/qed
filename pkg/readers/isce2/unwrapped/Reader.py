# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed

# dataset
from .Dataset import Dataset


# unwrapped interferograms contain one line interleaved {real32} complex dataset
# with a line of amplitudes, followed by a line of phases
class Reader(
    qed.flow.factory,
    family="qed.readers.isce2.unwwrapped",
    implements=qed.protocols.reader,
):
    """
    The reader of unwrapped interferograms
    """

    # public data
    uri = qed.properties.uri(scheme="file")
    uri.doc = "the uri of the data source"

    # the data layout
    cell = qed.protocols.datatype()
    cell.default = "real32"
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

        # unpack my state into a dataset configuration
        config = {
            "uri": self.uri,
            "cell": self.cell,
            "shape": self.shape,
        }

        # there is only one dataset in the file and it is structurally trivial; build it
        dataset = Dataset(name=f"{self.pyre_name}.data", **config)
        # and add it to the pile of datasets
        self.datasets.append(dataset)

        # all done
        return


# end of file
