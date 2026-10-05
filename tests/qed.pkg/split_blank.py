#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Split a viewport that shows nothing yet: the copy is blank as well, and the two stay independent
"""

# support
import qed


# split a blank viewport
def test():
    """
    Clone a viewport with no reader, and check that the clone is a blank viewport of its own
    """
    # a viewport, the way the store makes one before any reader is picked
    port = qed.ux.viewport(name="split_blank.port")
    # it shows nothing
    assert port.view().reader is None
    # make a copy, the way the store splits a viewport
    clone = port.clone()
    # the copy shows nothing either
    assert clone.view().reader is None
    # and it is a viewport of its own, with a view of its own
    assert clone is not port
    assert clone.view() is not port.view()
    # all done
    return clone


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
