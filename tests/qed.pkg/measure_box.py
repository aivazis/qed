#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise turning the two anchors of a measure path into the closed corners of a box
"""

# externals
import types

# support
import journal
import qed


# the box out of a pair of anchors
def box():
    """
    Exercise {View.measureMakeBox}: two opposite corners become the four corners of a closed box
    """
    # a measure path with two anchors, given as opposite corners in no particular order
    measure = qed.ux.measure(name="box.measure")
    measure.path = [(150, 260), (100, 200)]
    # that starts out clean
    measure.dirty = False
    # a stand-in view that holds it
    standin = types.SimpleNamespace(measure=measure, pyre_name="box.view")
    # make the box with the mutator borrowed from the view class
    qed.ux.view.measureMakeBox(standin)
    # the path holds the four corners, in order around the box from its top left
    assert measure.path == [(100, 200), (150, 200), (150, 260), (100, 260)], measure.path
    # all of them selected
    assert measure.selection == [0, 1, 2, 3]
    # the path is closed
    assert measure.closed is True
    # and the measure knows it has changed
    assert measure.dirty is True
    # all done
    return


# anything but two anchors is a change in client behavior
def miscount():
    """
    Exercise {View.measureMakeBox}: a path without exactly two anchors trips the firewall
    """
    # send the firewall reports to the trash, so they do not end up in the output of the test
    journal.firewall("qed.ux.store").device = journal.trash()
    # go through paths with the wrong number of anchors
    for path in ([], [(1, 2)], [(1, 2), (3, 4), (5, 6)]):
        # a measure that holds the path
        measure = qed.ux.measure(name=f"box.miscount.{len(path)}")
        measure.path = list(path)
        # a stand-in view that holds it
        standin = types.SimpleNamespace(measure=measure, pyre_name="box.view")
        # carefully
        try:
            # ask for a box
            qed.ux.view.measureMakeBox(standin)
        # the firewall should fire
        except journal.FirewallError:
            # and leave the path alone
            assert measure.path == list(path), measure.path
        # if it didn't
        else:
            # the check is missing
            assert False, f"no firewall for a path with {len(path)} anchors"
    # all done
    return


# main
if __name__ == "__main__":
    # run the checks
    box()
    miscount()


# end of file
