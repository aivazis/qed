#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Compare two acquisitions of the same frame side by side, with their paths synced, and check that
toggling the measure layer in one viewport turns it on or off in both, without changing the
reader either of them shows
"""

# externals
import os
import types

# support
import qed

# the raster in this directory
raster = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c16.dat")


def test():
    """
    Toggle the measure layer of two path synced viewports that show different readers
    """
    # two readers over the same raster stand in for two acquisitions of the same frame
    readers = {
        name: qed.readers.native.flat(name=name, uri=raster, shape=(65, 65), cell="c16")
        for name in ("measure_toggle.early", "measure_toggle.late")
    }
    # show each one in a viewport of its own
    ports = [
        qed.ux.viewport(
            name=f"measure_toggle.port.{index}",
            view=qed.ux.view(name=f"measure_toggle.view.{index}", reader=reader),
        )
        for index, reader in enumerate(readers.values())
    ]
    # get the views on display
    views = [port.view() for port in ports]
    # go through the views
    for view in views:
        # sync their paths
        view.sync.path = True
        # and turn on their measure layers, as turning on path syncing does
        view.measure.active = True

    # make a stand-in for the store that holds the viewports and can look up the readers
    store = types.SimpleNamespace(_viewports=ports, source=lambda name: readers[name])
    # and give it the store's own search for synced viewports
    store._syncedWith = lambda **kwds: qed.ux.store._syncedWith(store, **kwds)

    # toggle the layer of a viewport the way the client does, by naming the reader it shows
    def toggle(viewport):
        # get the name of the reader on display
        source = ports[viewport].view().reader.pyre_name
        # toggle, and collect the measure layers the store hands back
        return list(qed.ux.store.toggleMeasure(store, viewport=viewport, source=source))

    # check that each viewport still shows its own reader, with its layer in the given state
    def check(*states):
        # go through the viewports
        for port, view, reader, active in zip(ports, views, readers.values(), states):
            # each one still shows the view it started with
            assert port.view() is view, f"{port.pyre_name} switched views"
            # which still shows the same reader
            assert view.reader is reader, f"{port.pyre_name} switched to {view.reader.pyre_name}"
            # and has its layer in the expected state
            assert view.measure.active is active, f"{port.pyre_name}: {view.measure.active}"
        # all done
        return

    # turn the layer off in the second viewport
    measures = toggle(viewport=1)
    # it goes off in both, and neither viewport changes readers
    check(False, False)
    # the store hands back both layers, starting with the one that was toggled
    assert measures == [views[1].measure, views[0].measure]
    # turn the layer back on in the first viewport
    toggle(viewport=0)
    # and it comes back on in both
    check(True, True)

    # now let the two layers disagree
    views[0].measure.active = False
    # toggling the second viewport turns its layer off, and the first one follows it
    toggle(viewport=1)
    check(False, False)

    # take the first viewport out of the path sync group
    views[0].sync.path = False
    # and toggling the second viewport no longer affects it
    toggle(viewport=1)
    check(False, True)
    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
