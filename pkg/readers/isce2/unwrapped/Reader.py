# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import math
import qed
import journal

# metadata parser
from .. import xml

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

    selections = qed.properties.kv()
    selections.doc = "a key value store of preferred values for selectors"

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
            "cell": self.cell,
            "shape": self.shape,
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
        # build my availability map
        self.available = {}

        # all done
        return

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
            # if the width is missing but we know the height
            if shape[1] == 0 and shape[0]:
                # set it from the file size
                shape[1] = metadata.bytes / shape[0] / (2 * self.cell.bytes)
            # if the height is missing but we know the width
            if shape[0] == 0 and shape[1]:
                # set it from the file size
                shape[0] = metadata.bytes / shape[1] / (2 * self.cell.bytes)
            # if the shape is now fully resolved
            if (
                shape[0]
                and shape[1]
                and shape[0] == math.floor(shape[0])
                and shape[1] == math.floor(shape[1])
            ):
                # set it
                self.shape = tuple(shape)
            # if not
            else:
                # make a channel
                channel = journal.warning("qed.readers.unw")
                # generate a list of possible shapes
                channel.line(f"while attempting to load '{self.uri.address}'")
                channel.line(f"missing shape information; here are some possibilities")
                channel.line(f"as lines x samples")
                channel.indent()
                # generate some options
                for lines, samples in qed.libqed.factor(
                    product=metadata.bytes // (2 * self.cell.bytes), aspect=10
                ):
                    # and show them
                    channel.line(f"{lines} x {samples}")
                channel.outdent()
                channel.line(
                    f"please use '--lines' or '--samples' to provide the dataset shape"
                )
                # flush
                channel.log()

        # chain up
        yield from super().pyre_configured()
        # all done
        return


# end of file
