#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise the layout of the flow diagram: factories in flow order, left to right, and slots in
the order their factories declare them, with no two entities in the same place
"""

# support
import qed


# lay out the diagram of the phase channel
def test():
    """
    Build the diagram of the phase channel and check where its entities landed
    """
    # draw the flow of the phase channel
    diagram = qed.ux.diagram(name="diagram_layout.diagram", flow=qed.channels.phase())
    # the factories, left to right
    factories = sorted(diagram.factories, key=lambda entity: entity.position)
    # are the colormap and then the encoder
    assert [entity.factory.pyre_family() for entity in factories] == [
        "pyre.viz.colormaps.hsb",
        "pyre.viz.codecs.bmp",
    ]
    # a {spacing} apart along the horizontal axis
    assert [entity.position for entity in factories] == [(0, 0), (diagram.spacing, 0)]
    # every slot has a place of its own
    positions = [slot.position for slot in diagram.slots]
    assert len(positions) == len(set(positions))
    # and so does every factory, away from all the slots
    assert not set(entity.position for entity in factories) & set(positions)

    # the encoder declares its inputs as red, green, and blue
    encoder = factories[1]
    # so its input slots, each read by the encoder through one trait, stack in that order, top
    # to bottom
    inputs = sorted(
        (slot for slot in encoder.slots if slot.position[0] < encoder.position[0]),
        key=lambda slot: slot.position[1],
    )
    assert [trait.name for slot in inputs for trait in slot.readers[encoder]] == [
        "red",
        "green",
        "blue",
    ]

    # all done
    return diagram


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
