#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Exercise the look-at center that a view carries and that the store mutates per viewport
"""

# externals
import types

# support
import qed


# check the {Center} component's state, dirty tracking, clone, and reset
def center():
    """
    Exercise {Center}: defaults, dirty on modification, a faithful clone, and a reset to defaults
    """
    # a fresh center sits at the origin and is clean
    point = qed.ux.center(name="lookat.center")
    assert point.row == 0
    assert point.col == 0
    assert point.dirty is False

    # moving it marks it dirty
    point.row = 12.5
    point.col = 34.0
    assert point.dirty is True

    # a clone carries the same place
    twin = point.clone()
    assert twin.row == 12.5
    assert twin.col == 34.0

    # a reset to a set of defaults restores the place and marks it clean
    defaults = types.SimpleNamespace(row=0, col=0)
    point.reset(defaults=defaults)
    assert point.row == 0
    assert point.col == 0
    assert point.dirty is False

    # all done
    return


# check that a view records the look-at center it is told to
def lookAt():
    """
    Exercise {View.lookAt}: the (row, col) are written through to the view's center
    """
    # the mutator, borrowed from the view class
    setter = qed.ux.view.lookAt
    # a stand-in view with just a center
    standin = types.SimpleNamespace(center=types.SimpleNamespace(row=0, col=0))
    # aim it
    result = setter(standin, row=42.0, col=7.0)
    # the center moved
    assert standin.center.row == 42.0
    assert standin.center.col == 7.0
    # and the mutator returns the view, for chaining
    assert result is standin
    # all done
    return


# check that the store aims only the addressed viewport and hands back its center
def storeLookAt():
    """
    Exercise {Store.lookAt}: only the addressed viewport is moved; its center is returned
    """
    # the mutator, borrowed from the store class
    setter = qed.ux.store.lookAt

    # a record of which viewport was aimed
    calls = []

    # a stand-in viewport that delegates to a view carrying a center
    def makePort(tag):
        # the view this port wraps
        view = types.SimpleNamespace(
            center=types.SimpleNamespace(row=0, col=0, tag=tag)
        )

        # its look-at delegate records the call and moves the center
        def portLookAt(row, col):
            calls.append(tag)
            view.center.row = row
            view.center.col = col
            return view

        # hand back the port
        return types.SimpleNamespace(lookAt=portLookAt, _view=view)

    # a store stand-in with two viewports
    ports = [makePort(0), makePort(1)]
    standin = types.SimpleNamespace(_viewports=ports)

    # aim the second viewport
    result = setter(standin, viewport=1, row=100.0, col=200.0)

    # only the second viewport was touched
    assert calls == [1]
    # the first viewport stayed at the origin
    assert ports[0]._view.center.row == 0
    assert ports[0]._view.center.col == 0
    # the second viewport moved
    assert ports[1]._view.center.row == 100.0
    assert ports[1]._view.center.col == 200.0
    # and the returned center is the second viewport's
    assert result is ports[1]._view.center

    # all done
    return


# the driver
def test():
    """
    Check the look-at center component and its view/store mutators in isolation
    """
    # the component
    center()
    # the view mutator
    lookAt()
    # the store mutator
    storeLookAt()
    # all done
    return 0


# bootstrap
if __name__ == "__main__":
    # invoke the driver
    status = test()
    # and share the status with the shell
    raise SystemExit(status)


# end of file
