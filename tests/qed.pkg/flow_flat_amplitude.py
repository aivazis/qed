#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Render tiles of a flat file of complex values through the playground's pipeline, its reader
pinned to the flat reader of the file, and check that they match, byte for byte, the tiles the
iterators of the native amplitude channel render
"""

# externals
import cmath
import struct
import types

# support
import qed


# the driver
def test():
    """
    Stage the pipeline from a flat file and compare its tiles with the iterators'
    """
    # the shape of the file
    lines, samples = 40, 64
    # its cells, with magnitudes that wrap around every 17 cells, at phases that vary with the cell
    values = [cmath.rect(cell % 17, 0.05 * cell) for cell in range(lines * samples)]
    # write it, as interleaved pairs of single precision floats
    with open("flow_flat_amplitude.c8", "wb") as stream:
        # one cell at a time
        for value in values:
            # real and imaginary parts
            stream.write(struct.pack("<ff", value.real, value.imag))

    # a flat reader of it
    reader = qed.readers.native.flat(
        name="flow_flat_amplitude.reader",
        uri="flow_flat_amplitude.c8",
        cell="complex64",
        shape=(lines, samples),
    )
    # a store stand-in, with the recipe the pipeline starts from
    store = types.SimpleNamespace()
    store.amplitude = lambda: qed.ux.store.amplitude(store)
    # the pipeline the playground draws, with its reader pinned to this one
    recipe = qed.ux.store.pipeline(store, reader=reader)
    # stage it, which opens the file
    plan = recipe.stage()
    # the data the iterators read
    (dataset,) = reader.datasets
    # the range of magnitudes that maps onto [0,1]
    low, high = 0.0, 16.0

    # the tiles: their shape, their origin counted in strides, and their stride
    tiles = [((16, 16), (0, 0), (1, 1)), ((8, 16), (1, 0), (2, 2)), ((5, 8), (2, 1), (4, 4))]
    # go through them
    for shape, origin, stride in tiles:
        # realize the plan for the shape
        with plan.realize(shape=shape) as graph:
            # move the window
            graph["slice"].set(setting="origin", value=origin)
            graph["slice"].set(setting="stride", value=stride)
            # set the range
            graph["normalizer"].set(setting="interval", value=(low, high))
            # and pull the image
            flow = graph["image"].read()
        # the same tile through the iterators
        iterators = bytes(
            memoryview(
                qed.libqed.native.channels.amplitude(
                    source=dataset.data,
                    origin=origin,
                    shape=shape,
                    stride=stride,
                    min=low,
                    max=high,
                )
            )
        )
        # they match, byte for byte
        assert flow == iterators, (shape, origin, stride)
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
