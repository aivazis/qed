#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check the palette of the pipeline diagrams: one tray per protocol, in pipeline order, each one
starting with the protocol itself, followed by the classes that implement it
"""

# externals
import types

# support
import qed

# the resolvers are internal to the graphql package, so reach in
from qed.gql.QED import QED


# the driver
def test():
    """
    Describe the palette and check the trays and the levels of their entries
    """
    # a store stand-in, with the protocols the store offers
    store = types.SimpleNamespace()
    store.palette = lambda: qed.ux.store.palette(store)
    # describe the palette
    groups = QED.resolve_catalog(store, info=None)
    # there is a tray for each protocol, in the order the store offers them
    assert [group.family for group in groups] == [
        protocol.pyre_family() for protocol in store.palette()
    ]
    # go through the trays
    for group, protocol in zip(groups, store.palette()):
        # the first entry is the protocol itself
        first, *rest = group.entries
        assert first.family == protocol.pyre_family()
        # placed pinned to nothing
        assert first.level == "protocol"
        # and named the way the diagram names an unpinned factory
        assert first.name == protocol.__name__.lower()
        # the rest are classes
        assert all(entry.level == "class" for entry in rest)
        # sorted by family
        assert [entry.family for entry in rest] == sorted(entry.family for entry in rest)
    # the reader protocol exposes a raster, and reads nothing
    reader = groups[0].entries[0]
    assert reader.inputs == []
    assert reader.outputs == ["raster"]
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
