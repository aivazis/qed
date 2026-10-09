#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise the description of a factory that the inspector of the pipeline panel shows: its family,
its documentation, and its traits, sorted into inputs, outputs, and settings
"""

# support
import qed

# the description, as the graphql schema serves it
from qed.gql.diagram.FlowFactory import FlowFactory


# describe the factory of {flow} on a diagram of its own
def describe(name, flow):
    """
    Draw {flow} on a diagram of its own, and describe its only factory
    """
    # an empty diagram
    diagram = qed.ux.diagram(name=name, recipe=None)
    # with just this factory on it, pinned to the instance
    entity, *_ = diagram.addFactory(pin=flow, position=(0, 0, 0))
    # describe it
    return (
        FlowFactory.resolve_family(entity, None),
        FlowFactory.resolve_doc(entity, None),
        FlowFactory.resolve_traits(entity, None),
    )


# the gray colormap: slots, and no settings
def gray():
    """
    Describe the gray colormap
    """
    # describe it
    family, doc, traits = describe("diagram_inspector.gray", qed.viz.colormaps.gray()())
    # its family
    assert family == "pyre.viz.colormaps.gray"
    # its documentation, with the indentation of the source removed
    assert doc == "The colormap that turns a stream of values in [0,1] into gray scale"
    # its traits, in the order it declares them, sorted by what they are to it
    assert [(trait.name, trait.kind) for trait in traits] == [
        ("data", "input"),
        ("red", "output"),
        ("green", "output"),
        ("blue", "output"),
    ]
    # its slots hold tiles, each named by its specification: unit values in, color channels out
    assert [trait.type for trait in traits] == [
        "pyre.viz.tiles.unit",
        "pyre.viz.tiles.channel",
        "pyre.viz.tiles.channel",
        "pyre.viz.tiles.channel",
    ]
    # and each slot names the kind of product bound to it
    assert all(trait.value == "pyre.viz.tiles.heap" for trait in traits)
    # all done
    return


# the hl colormap: a setting, with its value and its default
def hl():
    """
    Describe the hl colormap, which has a setting
    """
    # make one, with its threshold away from its default; the foundry hands back the class, which
    # builds the factory
    flow = qed.viz.colormaps.hl()()
    flow.threshold = 0.25
    # describe it
    _, _, traits = describe("diagram_inspector.hl", flow)
    # find the setting
    (threshold,) = [trait for trait in traits if trait.kind == "setting"]
    # it is the threshold
    assert threshold.name == "threshold"
    # a float
    assert threshold.type == "float"
    # at the value it was given
    assert threshold.value == "0.25"
    # with its default
    assert threshold.default == "0.4"
    # all done
    return


# the driver
def test():
    """
    Describe a colormap without settings and one with
    """
    # the one without
    gray()
    # and the one with
    hl()
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
