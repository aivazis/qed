#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise the layout of the flow diagram: factories in flow order, left to right, slots in the
order their factories declare them, one slot for each product the factories share, and no two
entities in the same place; and check that a view keeps the diagram of its channel
"""

# externals
import types

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

    # the colormap and the encoder share the red, green, and blue products
    colormap = factories[0]
    # so each of them has one slot, written by the colormap and read by the encoder
    shared = [slot for slot in diagram.slots if slot.writers and slot.readers]
    assert len(shared) == 3
    assert all(set(slot.writers) == {colormap} for slot in shared)
    assert all(set(slot.readers) == {encoder} for slot in shared)
    # it sits on the side of the colormap
    assert all(slot.position[0] == colormap.position[0] + 5 for slot in shared)
    # carries the product the two factories share
    assert all(slot.bound for slot in shared)
    # and names it in a label the diagram knows about
    assert all(slot.labels and slot.labels <= diagram.labels for slot in shared)
    # which leaves the three inputs of the colormap, the three shared products, and the image
    assert len(diagram.slots) == 7

    # all done
    return diagram


# a view draws the diagram of its channel once
def persistent():
    """
    Ask a view for its diagram twice, and again after it changes channel
    """
    # the method, borrowed from the view class
    diagram = qed.ux.view.diagram
    # a stand-in view with a covariance channel, its table of flows, and no diagram yet
    standin = types.SimpleNamespace(
        channel=types.SimpleNamespace(pyre_name="diagram_layout.channel", tag="covariance"),
        flows=qed.ux.view.flows.fget(None),
        _diagram=(None, None),
    )
    # the first request draws it
    first = diagram(standin)
    # the second one gets the same diagram
    assert diagram(standin) is first
    # a new channel
    standin.channel = types.SimpleNamespace(pyre_name="diagram_layout.other", tag="covariance")
    # gets a diagram of its own
    assert diagram(standin) is not first
    # and a channel without a description
    standin.channel = types.SimpleNamespace(pyre_name="diagram_layout.none", tag="mystery")
    # gets none
    assert diagram(standin) is None
    # all done
    return first


# lay out the diagram of the covariance channel
def covariance():
    """
    Build the diagram of the covariance channel: normalizer, colormap, and encoder in a row
    """
    # draw the flow of the covariance channel
    diagram = qed.ux.diagram(name="diagram_layout.covariance", flow=qed.channels.covariance())
    # the factories, left to right
    factories = sorted(diagram.factories, key=lambda entity: entity.position)
    # are the normalizer, the colormap, and the encoder
    assert [entity.factory.pyre_family() for entity in factories] == [
        "pyre.viz.filters.parametric",
        "pyre.viz.colormaps.gray",
        "pyre.viz.codecs.bmp",
    ]
    # unpack them
    normalizer, gray, encoder = factories
    # the shared products: the normalized signal, and the three channels of color
    shared = [slot for slot in diagram.slots if slot.writers and slot.readers]
    # the normalized signal goes from the normalizer to the colormap
    assert [
        slot for slot in shared if set(slot.writers) == {normalizer} and set(slot.readers) == {gray}
    ]
    # and the colors from the colormap to the encoder
    assert len([s for s in shared if set(s.writers) == {gray} and set(s.readers) == {encoder}]) == 3
    # every slot has a place of its own
    positions = [slot.position for slot in diagram.slots]
    assert len(positions) == len(set(positions))
    # which leaves the input of the normalizer, the four shared products, and the image
    assert len(diagram.slots) == 6
    # all done
    return diagram


# main
if __name__ == "__main__":
    # run the tests
    test()
    persistent()
    covariance()


# end of file
