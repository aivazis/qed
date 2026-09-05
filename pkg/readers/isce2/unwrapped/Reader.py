# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


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

    # constants
    # my dataset can describe itself in a discovery record and materialize as a
    # metadata-only twin, so my first contact can happen on a crew member
    surveyable = True

    # interface
    @qed.export
    def open(self, measure=True):
        """
        Establish first contact with the data source: complete my shape, open the file,
        and build my dataset
        """
        # if i have already made contact
        if self._opened:
            # there is nothing further to do
            return self
        # leave a mark
        self._opened = True

        # make a timer that measures the layout discovery time
        discovery = qed.timers.wall(f"qed.profiler.discovery.{self.pyre_name}")
        # start it
        discovery.start()
        # complete my shape, interrogating the metadata for whatever is missing
        self._resolveShape()
        # stop the timer
        discovery.stop()

        # get my shape
        shape = self.shape
        # i need it fully resolved to continue
        if not shape or not shape[0] or not shape[1]:
            # bail; my configuration troubles have already been reported
            return self
        # the file must be large enough to hold the declared shape; each sample is a pair
        # of cells in the line interleaved layout, and a short file would let the render
        # machinery read past the end of the map and crash the process
        if not self._validateSize(shape=shape, cellsPerSample=2):
            # the complaint has been lodged
            return self

        # unpack my state into a dataset configuration
        config = {
            "uri": self.uri,
            "cell": self.cell,
            "shape": shape,
        }

        # make a timer that measures the amount of time it takes to collect statistics
        stats = qed.timers.wall(f"qed.profiler.stats.{self.pyre_name}")
        # and start it
        stats.start()
        # there is only one dataset in the file and it is structurally trivial; build it
        dataset = Dataset(name=f"{self.pyre_name}.data", **config)
        # stop the timer
        stats.stop()

        # add the dataset to the pile
        self.datasets.append(dataset)

        # unless my caller is a worker that will be handed the client's controller state,
        # let each dataset sample itself, so its channels start out tuned to its data
        if measure:
            # go through the datasets i discovered
            for dataset in self.datasets:
                # and let each one measure itself
                dataset.measure()

        # all done
        return self

    # metamethods
    def __init__(self, name, archive=None, **kwds):
        # chain up; construction is passive, so nothing touches the file until {open}
        super().__init__(name=name, **kwds)
        # initialize the availability map so the panel can render before first contact
        self.available = {}
        # all done
        return

    # implementation details
    def _resolveShape(self):
        """
        Complete my shape, interrogating the auxiliary metadata for whatever is missing
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
                channel.line(f"please use '--lines' or '--samples' to provide the dataset shape")
                # flush
                channel.log()

        # all done
        return

    def _validateSize(self, shape, cellsPerSample):
        """
        Check that my file is large enough to hold {shape} samples of {cellsPerSample}
        cells each
        """
        # compute the size the declared shape requires
        required = shape[0] * shape[1] * cellsPerSample * self.cell.bytes
        # measure the file
        actual = qed.primitives.path(self.uri.address).stat().st_size
        # if it holds enough
        if actual >= required:
            # we are good
            return True
        # otherwise, make a channel
        channel = journal.warning("qed.readers.unw")
        # complain
        channel.line(f"'{self.uri.address}' is too small for the declared shape")
        channel.line(f"shape {tuple(shape)} requires {required} bytes")
        channel.line(f"but the file holds only {actual}")
        # flush
        channel.log()
        # and reject
        return False

    # private data
    _opened = False  # whether first contact has been made


# end of file
