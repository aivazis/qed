# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


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

        # get my cell
        cell = self.cell
        # and my shape
        shape = self.shape
        # i need both to continue
        if not cell or not shape:
            # so bail, if they are not fully configured
            return

        # unpack my state into a dataset configuration
        config = {
            "uri": self.uri,
            "shape": shape,
            "cell": cell,
            "tile": self.cell.tile,
        }

        # make a timer that measures the amount of time it takes to collect statistics
        stats = qed.timers.wall(f"qed.profiler.stats.{name}")
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
        # build my availability map
        self.available = {}

        # all done
        return

    # framework hooks
    def pyre_configured(self):
        """
        Hook invoked after the reader configuration is complete
        """
        # get my uri
        uri = self.uri
        # convert its address into a path
        path = qed.primitives.path(uri.address)
        # get the file size
        filesize = path.stat().st_size
        # get my cell
        cell = self.cell
        # if i don't have
        if not cell:
            # make a channel
            channel = journal.error("qed.readers.native.flat")
            # complain
            channel.line(f"could not load a dataset from '{uri.address}'")
            channel.line(f"missing data type specification")
            channel.line(f"please provide a value for '--cell'")
            # flush
            channel.log()
            # just in case errors aren't fatal
            yield f"missing cell specification for '{uri.address}'"
            # and bail
            return
        # get the current value of my shape
        shape = list(self.shape) if self.shape else [0, 0]
        # if it's trivial
        if not shape or shape[0] == 0 or shape[1] == 0:
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

        # chain up
        yield from super().pyre_configured()
        # all done
        return


# end of file
