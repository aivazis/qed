#! /usr/bin/env python3
# -*- python -*-
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


# check that the store aims the addressed viewport, and the ones that scroll in sync with it
def storeLookAt():
    """
    Exercise {Store.lookAt}: the addressed viewport is moved and its center returned; the
    viewports that scroll in sync with it follow, shifted by the difference of their offsets
    """
    # the mutator, borrowed from the store class
    setter = qed.ux.store.lookAt

    # a record of which viewport was aimed
    calls = []

    # a stand-in viewport that delegates to a view carrying a center and a sync state
    def makePort(tag, scroll, offsets):
        # the view this port wraps
        view = types.SimpleNamespace(
            center=types.SimpleNamespace(row=0, col=0, tag=tag),
            sync=types.SimpleNamespace(scroll=scroll, offsets=offsets),
        )

        # its look-at delegate records the call and moves the center
        def portLookAt(row, col):
            calls.append(tag)
            view.center.row = row
            view.center.col = col
            return view

        # hand back the port
        return types.SimpleNamespace(lookAt=portLookAt, view=lambda: view, _view=view)

    # a store stand-in over the given ports, with the store's own search for synced viewports
    def makeStore(ports):
        # the stand-in
        store = types.SimpleNamespace(_viewports=ports)
        # borrow the search
        store._syncedWith = lambda **kwds: qed.ux.store._syncedWith(store, **kwds)
        # and hand it back
        return store

    # two viewports that do not scroll in sync
    ports = [makePort(0, False, (0, 0)), makePort(1, False, (0, 0))]
    # aim the second one
    result = setter(makeStore(ports), viewport=1, row=100.0, col=200.0)
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

    # start over, with three viewports: two that scroll in sync, with offsets (x, y), and one that
    # does not
    calls.clear()
    ports = [makePort(0, True, (5, 3)), makePort(1, True, (1, 1)), makePort(2, False, (0, 0))]
    # aim the second one
    result = setter(makeStore(ports), viewport=1, row=100.0, col=200.0)
    # the second viewport moved, and its synced peer followed; the third stayed put
    assert sorted(calls) == [0, 1]
    # the second viewport is where it was sent
    assert (ports[1]._view.center.row, ports[1]._view.center.col) == (100.0, 200.0)
    # its peer is shifted by the difference of the offsets: rows by y, columns by x
    assert (ports[0]._view.center.row, ports[0]._view.center.col) == (102.0, 204.0)
    # the one that does not scroll in sync stayed at the origin
    assert (ports[2]._view.center.row, ports[2]._view.center.col) == (0, 0)
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
