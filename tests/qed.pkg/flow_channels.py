#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Render tiles through every native channel that has a recipe, once with its iterators and once
with the pipeline of its recipe, and check that they match byte for byte, over every cell type the
channel reads, several windows and strides, and several settings of its controllers
"""

# externals
import cmath
import types
import uuid

# support
import qed

# the extent of the rasters
rows, columns = 37, 53
# the tiles: origin, shape, and stride, in decimated cells; a stride is a power of two along each
# axis, since it comes from a zoom level
TILES = [
    # a square piece
    ((3, 4), (16, 16), (1, 1)),
    # a piece taller than it is wide, whose lines need padding
    ((2, 1), (9, 5), (2, 4)),
    # and one wider than it is tall
    ((1, 2), (5, 7), (4, 2)),
]


# a raster of {cell} holding {value} of each cell number
def raster(cell, value):
    """
    Make a dataset stand-in over a grid of {cell} that holds {value} of each cell number
    """
    # make the grid
    grid = qed.libpyre.grid.heap(shape=[rows, columns], cell=cell)
    # fill it
    for at in range(rows * columns):
        # one cell at a time
        grid[divmod(at, columns)] = value(at)
    # and wrap it in a dataset stand-in, which is what a channel reads
    return types.SimpleNamespace(data=grid)


# compare the two engines of {channel} over the tiles of {source}, each time after {configure}
def compare(channel, source, configurations):
    """
    Render every tile of {source} through both engines of {channel}, under each of the
    {configurations}, and check that they agree byte for byte
    """
    # go through the configurations
    for configure in configurations:
        # apply it
        configure(channel)
        # go through the tiles
        for origin, shape, stride in TILES:
            # the zoom levels that make the stride, which is a power of two along each axis
            zoom = tuple(s.bit_length() - 1 for s in stride)
            # render with the iterators
            channel.engine = "iterators"
            expected = bytes(
                memoryview(channel.tile(source=source, zoom=zoom, origin=origin, shape=shape))
            )
            # and with the pipeline
            channel.engine = "flow"
            rendered = channel.tile(source=source, zoom=zoom, origin=origin, shape=shape)
            # they must agree
            assert rendered == expected, (channel.tag, origin, shape, stride)
    # all done
    return


# make a channel of the given {kind}
def channel(kind):
    """
    Make a native channel of the given {kind}, under a name of its own
    """
    # pyre hands back the old instance for a name it has seen before
    return getattr(qed.readers.native.channels, kind)(name=f"flow_channels.{kind}.{uuid.uuid1()}")


# the driver
def test():
    """
    Compare the engines of the channels over reals and over complex values
    """
    # the cell types of reals, and the values each one can hold
    reals = {
        "int8": lambda i: i % 120 - 60,
        "uint8": lambda i: i % 250,
        "int16": lambda i: i % 3000 - 1500,
        "uint16": lambda i: i % 6000,
        "int32": lambda i: 7 * i - 5000,
        "uint32": lambda i: 7 * i,
        "int64": lambda i: 11 * i - 9000,
        "uint64": lambda i: 11 * i,
        "float32": lambda i: 0.25 * i - 100.0,
        "float64": lambda i: 0.125 * i - 50.0,
    }

    # the ranges of a linear controller
    def ranged(low, high):
        """
        Set the range of the controller of a channel
        """

        # the configuration
        def configure(channel):
            # set the range
            channel.range.low = low
            channel.range.high = high
            # all done
            return

        # hand it off
        return configure

    # the value channel over every cell type of reals
    for cell, value in reals.items():
        # compare its engines
        compare(
            channel=channel("value"),
            source=raster(cell=cell, value=value),
            configurations=[ranged(-50.0, 150.0), ranged(0.0, 1000.0), ranged(-3000, 3000)],
        )

    # complex values: magnitudes that wrap every 17 cells, at phases that vary with the cell
    value = lambda i: cmath.rect(i % 17, 0.05 * i)

    # the decades of the amplitude
    def decades(low, high):
        """
        Set the range of the amplitude of a channel, in decades
        """

        # the configuration
        def configure(channel):
            # set the range
            channel.amplitude.low = low
            channel.amplitude.high = high
            # all done
            return

        # hand it off
        return configure

    # the range of the phase, and the constant parts of the color
    def wheel(low, high, saturation, brightness=None):
        """
        Set the range of the phase of a channel, and its saturation and brightness
        """

        # the configuration
        def configure(channel):
            # set the range of the phase
            channel.phase.low = low
            channel.phase.high = high
            # the saturation
            channel.saturation.value = saturation
            # and the brightness, if the channel has one
            if brightness is not None:
                # set it
                channel.brightness.value = brightness
            # all done
            return

        # hand it off
        return configure

    # go through the complex cell types
    for cell in ("complex64", "complex128"):
        # the raster
        source = raster(cell=cell, value=value)
        # the amplitude
        compare(
            channel=channel("amplitude"),
            source=source,
            configurations=[decades(-1, 1.25), decades(0, 2)],
        )
        # the real and the imaginary parts
        for kind in ("real", "imaginary"):
            # compare
            compare(
                channel=channel(kind),
                source=source,
                configurations=[ranged(-16, 16), ranged(-4, 8)],
            )
        # the phase
        compare(
            channel=channel("phase"),
            source=source,
            configurations=[wheel(0, 1, 1, 1), wheel(0.25, 0.75, 0.5, 0.8)],
        )

        # the whole complex value
        def complete(low, high, phaseLow, phaseHigh, saturation):
            """
            Set the amplitude, the phase, and the saturation of a complex channel
            """

            # the configuration
            def configure(channel):
                # the amplitude
                decades(low, high)(channel)
                # the phase and the saturation
                wheel(phaseLow, phaseHigh, saturation)(channel)
                # all done
                return

            # hand it off
            return configure

        # compare
        compare(
            channel=channel("complex"),
            source=source,
            configurations=[complete(-1, 1.25, 0, 1, 0.5), complete(0, 2, 0.1, 0.9, 1)],
        )

    # one channel over two datasets of the same cells, the way the blocks of a file of records
    # reach it, reuses the graphs it realized for the first one
    shared = channel("value")
    # so the second dataset must reach the pipeline
    for value in (lambda i: 0.5 * i - 20, lambda i: (i * 37) % 101):
        # and render the same way the iterators render it
        compare(
            channel=shared,
            source=raster(cell="float32", value=value),
            configurations=[ranged(-20.0, 100.0)],
        )

    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
