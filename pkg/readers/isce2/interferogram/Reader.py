# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed

# my dataset
from .Dataset import Dataset


# interferograms are flat complex datasets
class Reader(
    qed.flow.factory,
    family="qed.readers.isce2.interferogram",
    implements=qed.protocols.reader,
):
    """
    The interferogram reader
    """

    # public data
    uri = qed.properties.uri(scheme="file")
    uri.doc = "the uri of the data source"

    cell = qed.protocols.datatype()
    cell.default = "complex64"
    cell.doc = "the type of the dataset payload"

    shape = qed.properties.tuple(schema=qed.properties.int())
    shape.doc = "the size of the dataset in (lines, samples)"

    selectors = qed.protocols.selectors()
    selectors.default = {}
    selectors.doc = "a map of selector names to their allowed values"

    datasets = qed.properties.list(schema=qed.protocols.dataset.output())
    datasets.doc = "the list of data sets provided by the reader"

    # metamethods
    def __init__(self, name, **kwds):
        # make a timer that measures the layout discovery time
        discovery = qed.timers.wall(f"qed.profiler.discovery.{name}")
        # start the discovery timer
        discovery.start()
        # chain up
        super().__init__(name=name, **kwds)
        # stop the discovery timer
        discovery.stop()

        # unpack my state into a dataset configuration
        config = {
            "uri": self.uri,
            "shape": self.shape,
            "cell": self.cell,
            "tile": self.cell.tile,
        }

        # make a timer that measures the amount of time it takes to collect statistics
        stats = qed.timers.wall(f"qed.profiler.stats.{name}")
        # and start it
        stats.start()
        # there is only one dataset in the file and it is structurally trivial; build it
        dataset = Dataset(name=f"{self.pyre_name}.data", **config)
        # stop the timer
        stats.stop()

        # add the dataset to the pile
        self.datasets.append(dataset)

        # all done
        return


# end of file
