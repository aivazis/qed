# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import math
import qed
import journal


# a reader of flat binary files
class Flat(
    qed.flow.factory, family="qed.readers.native.flat", implements=qed.protocols.reader
):
    """
    A reader of flat binary files
    """

    # public data
    uri = qed.properties.uri(scheme="file")
    uri.doc = "the uri of the data source"

    cell = qed.protocols.datatype()
    cell.default = None
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
        # complete my shape, interrogating the file for whatever is missing
        self._resolveShape()
        # stop the timer
        discovery.stop()

        # get my cell
        cell = self.cell
        # and my shape
        shape = self.shape
        # i need a cell and a fully resolved shape to continue
        if not cell or not shape or not shape[0] or not shape[1]:
            # bail; my configuration troubles have already been reported
            return self
        # the file must be large enough to hold the declared shape; a short file would let
        # the render machinery read past the end of the map and crash the process
        if not self._validateSize(cell=cell, shape=shape, cellsPerSample=1):
            # the complaint has been lodged
            return self

        # unpack my state into a dataset configuration
        config = {
            "uri": self.uri,
            "shape": shape,
            "cell": cell,
            "tile": self.cell.tile,
        }

        # make a timer that measures the amount of time it takes to collect statistics
        stats = qed.timers.wall(f"qed.profiler.stats.{self.pyre_name}")
        # and start it
        stats.start()
        # there is only one dataset in the file and it is structurally trivial; build it
        dataset = qed.readers.native.datasets.mmap(
            name=f"{self.pyre_name}.data", **config
        )
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
        Complete my shape, interrogating the file for whatever is missing
        """
        # get my cell
        cell = self.cell
        # if i don't have one
        if not cell:
            # make a channel
            channel = journal.error("qed.readers.native.flat")
            # complain
            channel.line(f"could not load a dataset from '{self.uri.address}'")
            channel.line(f"missing data type specification")
            channel.line(f"please provide a value for '--cell'")
            # flush
            channel.log()
            # and bail
            return
        # get the current value of my shape
        shape = list(self.shape) if self.shape else [0, 0]
        # if it is already fully resolved
        if shape and shape[0] and shape[1]:
            # there is nothing to infer
            return
        # get my uri
        uri = self.uri
        # convert its address into a path
        path = qed.primitives.path(uri.address)
        # get the file size
        filesize = path.stat().st_size
        # if the width is missing but we know the height
        if shape[1] == 0 and shape[0]:
            # set it from the file size
            shape[1] = filesize / shape[0] / cell.bytes
        # if the height is missing but we know the width
        if shape[0] == 0 and shape[1]:
            # set it from the file size
            shape[0] = filesize / shape[1] / cell.bytes
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
                product=filesize // cell.bytes, aspect=10
            ):
                # and show them
                channel.line(f"{lines} x {samples}")
            channel.outdent()
            channel.line(
                f"please use '--lines' or '--samples' to provide the dataset shape"
            )
            # flush
            channel.log()
        # all done
        return

    def _validateSize(self, cell, shape, cellsPerSample):
        """
        Check that my file is large enough to hold {shape} samples of {cellsPerSample}
        {cell} instances each
        """
        # compute the size the declared shape requires
        required = shape[0] * shape[1] * cellsPerSample * cell.bytes
        # measure the file
        actual = qed.primitives.path(self.uri.address).stat().st_size
        # if it holds enough
        if actual >= required:
            # we are good
            return True
        # otherwise, make a channel
        channel = journal.warning("qed.readers.native.flat")
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
