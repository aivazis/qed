#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a view draws its tiles with the engine it is asked for: the pipeline of its channel's
recipe when that can draw the dataset, the fused iterators otherwise, and that every change of
engine asks for the tiles again
"""

# externals
import types

# support
import journal
import qed


# the driver
def test():
    """
    Switch the engine of a view back and forth, and try the switches it must refuse
    """
    # the refusals below are reported on a warning channel; this driver expects them
    journal.warning("qed.ux.engines").deactivate()
    # build the app and the store over the configuration of this directory
    app = qed.shells.qed(name="qed.app")
    ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.virtual(), pfs=app.pfs)
    store = ux.store
    store.open()
    # the reader, and the view of the first viewport
    reader, *_ = store.sources
    view = store._viewports[0].view()
    # show the amplitude of its dataset
    list(store.channelSet(viewport=0, source=reader.pyre_name, tag="amplitude"))
    # the channel the view shows
    channel = view.channel
    assert channel.tag == "amplitude"

    # the amplitude of complex cells in host byte order has a pipeline that can draw them
    assert view.flowable()
    # and it is the default engine
    assert view.engine() == "flow"

    # switch to the iterators
    session = view.session
    (changed,) = store.engineSet(viewport=0, engine="iterators")
    # the store hands back the view it changed
    assert changed is view
    # which now draws with the iterators
    assert view.engine() == "iterators"
    assert channel.engine == "iterators"
    # and asks for its tiles again
    assert view.session != session

    # and back to the pipeline
    session = view.session
    store.engineSet(viewport=0, engine="flow")
    assert view.engine() == "flow"
    assert view.session != session

    # an engine nobody knows changes nothing
    session = view.session
    store.engineSet(viewport=0, engine="gpu")
    assert view.engine() == "flow"
    assert view.session == session

    # the pipeline decides from the description of a dataset alone: cells in the host's order
    native = types.SimpleNamespace(cell=types.SimpleNamespace(byteswap=False))
    # it can draw
    assert channel.flows(source=native)
    # cells in the order the host lacks
    swapped = types.SimpleNamespace(cell=types.SimpleNamespace(byteswap=True))
    # it cannot
    assert not channel.flows(source=swapped)
    # nor the tiles of a dataset that draws them with a kernel of its own, the way gdal bands do
    assert not channel.flows(source=types.SimpleNamespace(flow=False))

    # a channel whose pipeline cannot draw the dataset, e.g. one without a recipe
    view.channel.flows = lambda source: False
    # draws with the iterators whatever its engine says
    assert not view.flowable()
    assert view.engine() == "iterators"
    # pick the iterators
    store.engineSet(viewport=0, engine="iterators")
    # and asking for the pipeline is refused, leaving the tiles alone
    session = view.session
    store.engineSet(viewport=0, engine="flow")
    assert channel.engine == "iterators"
    assert view.engine() == "iterators"
    assert view.session == session

    # all done
    return


# main
if __name__ == "__main__":
    # run the test
    test()


# end of file
