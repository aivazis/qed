#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Render tiles through every channel of the isce2 interferograms and unwrapped interferograms,
once with its iterators and once with the pipeline of its recipe, and check that they match byte
for byte, over the cell types the channel reads, several windows and strides, and several
settings of its controllers
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


# an interferogram of {cell} holding {value} of each cell number
def interferogram(cell, value):
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


# an unwrapped interferogram of {cell}, with {amplitude} and {phase} of each cell number
def unwrapped(cell, amplitude, phase):
    """
    Make a dataset stand-in over a line interleaved grid of {cell} that holds the {amplitude}
    and the {phase} of each cell number in its two bands
    """
    # make the grid
    grid = qed.libpyre.grid.heap(shape=[rows, 2, columns], cell=cell)
    # fill it
    for at in range(rows * columns):
        # the line and the sample
        line, sample = divmod(at, columns)
        # the amplitude band
        grid[(line, 0, sample)] = amplitude(at)
        # and the phase band
        grid[(line, 1, sample)] = phase(at)
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
            assert rendered == expected, (channel.pyre_name, origin, shape, stride)
    # all done
    return


# make a channel of the given {kind} from the channels of {family}
def channel(family, kind):
    """
    Make a channel of the given {kind} from {family}, under a name of its own
    """
    # pyre hands back the old instance for a name it has seen before
    return getattr(family, kind)(name=f"flow_isce2.{kind}.{uuid.uuid1()}")


# the driver
def test():
    """
    Compare the engines of the channels of interferograms and unwrapped interferograms
    """
    # the channels of interferograms
    ints = qed.readers.isce2.interferogram.channels
    # and of unwrapped interferograms
    unws = qed.readers.isce2.unwrapped.channels

    # the range of a linear controller
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

    # the range of the phase
    def phased(low, high):
        """
        Set the range of the phase of a channel
        """

        # the configuration
        def configure(channel):
            # set the range
            channel.phase.low = low
            channel.phase.high = high
            # all done
            return

        # hand it off
        return configure

    # the brightness
    def bright(value):
        """
        Set the brightness of a channel
        """

        # the configuration
        def configure(channel):
            # set it
            channel.brightness.value = value
            # all done
            return

        # hand it off
        return configure

    # the power law
    def power(mean, scale, exponent):
        """
        Set the power law of a channel
        """

        # the configuration
        def configure(channel):
            # the mean amplitude
            channel.mean = mean
            # the scale
            channel.scale.value = scale
            # and the exponent
            channel.exponent.value = exponent
            # all done
            return

        # hand it off
        return configure

    # several configurations at once
    def both(*configurations):
        """
        Apply all {configurations} to a channel
        """

        # the configuration
        def configure(channel):
            # go through them
            for configuration in configurations:
                # one at a time
                configuration(channel)
            # all done
            return

        # hand it off
        return configure

    # complex values: magnitudes that wrap every 17 cells, at phases that vary with the cell
    value = lambda i: cmath.rect(i % 17, 0.05 * i)
    # go through the complex cell types
    for cell in ("complex64", "complex128"):
        # the interferogram
        source = interferogram(cell=cell, value=value)
        # the amplitude
        compare(
            channel=channel(ints, "amplitude"),
            source=source,
            configurations=[decades(-1, 1.25), decades(0, 2)],
        )
        # the real and the imaginary parts
        for kind in ("real", "imaginary"):
            # compare
            compare(
                channel=channel(ints, kind),
                source=source,
                configurations=[ranged(-16, 16), ranged(-4, 8)],
            )
        # the phase
        compare(
            channel=channel(ints, "phase"),
            source=source,
            configurations=[both(phased(0, 1), bright(1)), both(phased(0.25, 0.75), bright(0.6))],
        )
        # the whole complex value
        compare(
            channel=channel(ints, "complex"),
            source=source,
            configurations=[
                both(decades(-1, 1.25), phased(0, 1)),
                both(decades(0, 2), phased(0.1, 0.9)),
            ],
        )

    # amplitudes that wrap every 23 cells, and phases that sweep a few turns
    amplitude = lambda i: 0.5 + i % 23
    phase = lambda i: 0.01 * i - 3.0
    # go through the cell types of unwrapped interferograms
    for cell in ("float32", "float64"):
        # the unwrapped interferogram
        source = unwrapped(cell=cell, amplitude=amplitude, phase=phase)
        # the amplitude
        compare(
            channel=channel(unws, "amplitude"),
            source=source,
            configurations=[power(1, 1, 1), power(11.5, 0.5, 0.3)],
        )
        # the phase
        compare(
            channel=channel(unws, "phase"),
            source=source,
            configurations=[
                both(phased(-3, 6), bright(0.5)),
                both(phased(-1, 1), bright(0.9)),
            ],
        )
        # the whole complex value
        compare(
            channel=channel(unws, "complex"),
            source=source,
            configurations=[
                both(power(1, 1, 1), phased(-3, 6)),
                both(power(11.5, 0.5, 0.3), phased(-1, 1)),
            ],
        )

    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
