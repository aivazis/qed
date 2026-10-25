#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Every trait of a factory reads as text, or as nothing, whatever class from the palette the factory
is pinned to: a class has the defaults its traits are declared with, some of which are classes of
components, e.g. the cell of a reader of interferograms, whose instance properties mean nothing yet
"""

# externals
import uuid

# support
import qed
from qed.gql.diagram.FlowFactory import FlowFactory


# the driver
def test() -> None:
    """
    Pin a factory to each class the palette offers, and read its traits
    """
    # the classes the palette offers, under each of its protocols
    classes = []
    # go through the protocols
    for protocol in qed.ux.store.palette(None):
        # and their implementers
        for _, _, implementer in protocol.pyre_locateAllImplementers(namespace="pyre"):
            # a foundry hands out the class it stands for
            cls = implementer() if isinstance(implementer, qed.foundry) else implementer
            # keep it, once
            if cls not in classes:
                # add it to the pile
                classes.append(cls)
    # there are plenty of them
    assert len(classes) > 10, len(classes)
    # an empty diagram, under a name of its own: pyre hands back the old instance for a name it
    # has seen before
    diagram = qed.ux.diagram(name=f"diagram_traits.{uuid.uuid1()}", recipe=None)
    # go through the classes, each on a spot of its own
    for row, cls in enumerate(classes):
        # place a factory pinned to it
        factory, *_ = diagram.addFactory(pin=cls, position=(0, 40 * row, 0))
        # read its traits
        for trait in FlowFactory.resolve_traits(factory, None):
            # each value and default is text, or nothing
            for text in (trait.value, trait.default):
                # so check it
                assert text is None or isinstance(text, str), (cls.pyre_family(), trait.name, text)
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
