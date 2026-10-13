#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
The labels of a diagram carry their parts, each one missing when it does not apply: a factory
or a product pinned to an instance is labeled by the name of the instance and the family of its
class, one pinned to a class by the family alone, and a connector by the names of its traits
"""

# support
import qed


# label the diagram of the amplitude channel
def test() -> None:
    """
    Draw the flow of the amplitude channel and check the parts of its labels
    """
    # draw the flow of the amplitude channel, as a recipe pinned to its instances
    diagram = qed.ux.diagram(
        name="diagram_labels.diagram",
        recipe=qed.flow.recipe.harvest(flow=qed.channels.amplitude()),
    )

    # every factory is pinned to an instance
    for factory in diagram.factories:
        # so its label has the name of the instance and the family of its class
        (label,) = [label for label in factory.labels if label.category == "factory"]
        # get the instance
        pin = factory.node.pin
        # check
        assert (label.given, label.family) == (pin.pyre_name, type(pin).pyre_family())
        # and it says nothing a connector would
        assert label.traits == [], label.traits

    # the slots whose products are pinned get a label
    pinned = [slot for slot in diagram.slots if slot.product is not None and slot.product.pin]
    # there are some
    assert pinned
    # go through them
    for slot in pinned:
        # find the label of the product
        (label,) = [label for label in slot.labels if label.category == "product"]
        # get the instance
        pin = slot.product.pin
        # its parts are the name of the instance and the family of its class
        assert (label.given, label.family) == (pin.pyre_name, type(pin).pyre_family())
        # it has no protocol role
        assert label.role is None, label.role

    # a product pinned to a class instead
    slot = pinned[0]
    # repin it
    slot.product.pin = type(slot.product.pin)
    # and draw its label again
    (label,) = [label for label in slot.generateLabels() if label.category == "product"]
    # has no name to give, only the family
    assert (label.given, label.family) == (None, slot.product.pin.pyre_family()), label.given

    # the connectors are labeled by the names of their traits
    for connector in diagram.connectors:
        # every one of them
        assert connector.traitLabel.traits == [trait.name for trait in connector]
        # and nothing else
        assert (connector.traitLabel.given, connector.traitLabel.family) == (None, None)

    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
