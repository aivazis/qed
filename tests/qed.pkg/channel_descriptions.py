#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise the flows that describe what the channels of the readers compute: the ones painted gray
lay out their factories in the order the c++ pipelines apply them, and every reader channel names
the flow that describes it, or admits there is none yet
"""

# externals
import uuid

# support
import qed


# the factories of the diagram of {flow}, left to right
def factories(flow):
    """
    Draw {flow} and list the families of its factories in the order they are laid out
    """
    # draw it, under a name of its own
    diagram = qed.ux.diagram(name=f"channel_descriptions.{uuid.uuid1()}", flow=flow())
    # sort the factories by where they are
    ordered = sorted(diagram.factories, key=lambda factory: factory.position)
    # and name them
    return [factory.factory.pyre_family() for factory in ordered]


# the flows painted gray
def gray():
    """
    Check the order of the factories of the flows that paint a signal gray
    """
    # the stages after the selector
    tail = ["pyre.viz.normalizers.parametric", "pyre.viz.colormaps.gray", "pyre.viz.encoders.bmp"]
    # a value goes straight to the normalizer
    assert factories(qed.channels.value) == tail
    # the amplitude computes the magnitude of a complex signal first
    assert factories(qed.channels.amplitude) == ["pyre.viz.operators.amplitude"] + tail
    # the others pick a part of a complex signal first
    for name in ["real", "imaginary"]:
        # draw it
        assert factories(getattr(qed.channels, name)) == [f"pyre.viz.selectors.{name}"] + tail
    # all done
    return


# the descriptions the reader channels name
def readers():
    """
    Check the flow that each reader channel names as its description
    """
    # the channels, and the flows that describe them
    expected = {
        qed.readers.native.channels.value: qed.channels.value,
        qed.readers.native.channels.abs: qed.channels.amplitude,
        qed.readers.native.channels.amplitude: qed.channels.amplitude,
        qed.readers.native.channels.real: qed.channels.real,
        qed.readers.native.channels.imaginary: qed.channels.imaginary,
        qed.readers.native.channels.phase: qed.channels.phase,
        qed.readers.native.channels.complex: None,
    }
    # go through them
    for channel, flow in expected.items():
        # and check
        assert channel.description() is flow, channel
    # all done
    return


# the driver
def test():
    """
    Check the flows painted gray, and what the reader channels name
    """
    # the flows
    gray()
    # and the readers
    readers()
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
