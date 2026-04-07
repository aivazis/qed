#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal


# the driver
class Fetch(qed.application, family="qed.apps.perf.fetch"):
    """
    Measure tile creation performance
    """

    # the path to the file
    uri = qed.properties.uri()
    uri.default = "rslc.h5"
    uri.doc = "the path to the sample file, assumed to be a NISAR RSLC"

    # interface
    @qed.export
    def main(self, *args, **kwds):
        """
        The main entry point
        """
        # open the file
        rslc = qed.h5.read(uri=str(self.uri))
        # navigate to the {HH} dataset
        hh = rslc.science.LSAR.RSLC.swaths.frequencyA.HH
        # zoom
        self.zoom(dataset=hh, level=0)
        # all done
        return 0

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # make a couple of timers
        self.wall = qed.timers.wall("qed.perf.fetch.wall")
        self.cpu = qed.timers.cpu("qed.perf.fetch.cpu")
        # and a channel
        self.channel = journal.info("qef.perf.fetch")
        # all done
        return

    # implementation details
    def zoom(self, dataset, level=0):
        """
        Generate a tile at the given zoom {level}
        """
        # get my channel
        channel = self.channel
        # and my timers
        wall = self.wall
        cpu = self.cpu

        # pick a starting location
        origin = qed.libpyre.grid.Index2D(index=(0, 0))
        # report
        channel.log(f"origin: {origin}")

        # if the dataset is chunked
        if dataset.dcpl.getLayout().name == "chunked":
            # get its rank
            rank = len(dataset.shape)
            # and use the chunk shape as the tile shape
            tile = dataset.dcpl.getChunk(rank=rank)
            # report
            channel.log(f"chunked; using tile: {tile}")
        # otherwise
        else:
            # set the tile to 512 x 512
            tile = 512, 512
            # report
            channel.log(f"not chunked; using tile: {tile}")
        # turn this in to a grid shape
        shape = qed.libpyre.grid.Shape2D(shape=tile)
        # report
        channel.log(f"shape: {shape}")

        # build the grid layout
        packing = qed.libpyre.grid.Canonical2D(shape=shape)
        # allocate the storage
        storage = qed.libpyre.memory.ComplexFloatHeap(cells=shape.cells)
        # make a grid
        grid = qed.libpyre.grid.ComplexFloatHeapGrid2D(packing=packing, storage=storage)
        # report
        channel.log(f"grid: {grid}")

        # start the timers
        wall.start()
        cpu.start()

        # read the data
        dataset.read()

        # stop the timers
        cpu.stop()
        wall.stop()

        # report
        channel.line(f"zoom: {level}")
        channel.indent()
        channel.line(f"in {cpu.ms():.3f} ms ({cpu.type})")
        channel.line(f"in {wall.ms():.3f} ms ({wall.type})")
        channel.outdent()
        # flush
        channel.log()

        # all done
        return 0


# bootstrap
if __name__ == "__main__":
    # instantiate
    app = Fetch(name="fetch")
    # invoke the driver
    status = app.run()
    # and share the status with the shell
    raise SystemExit(status)


# end of file
