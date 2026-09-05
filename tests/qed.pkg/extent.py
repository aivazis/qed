#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the store routes controller updates and hand-set display bounds correctly: a drag
payload moves the picks and lets its extent ride along only when it accommodates them, while a
resize moves only the bounds, never the picks or the session token, and refuses to encroach
"""

# support
import qed
import journal

# the refusals below are reported on channels that would otherwise break the silence
journal.warning("qed.ux.controllers").device = journal.trash()
journal.error("qed.ux.controllers").device = journal.trash()

# load the app so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# build its dispatcher, which assembles the store with the local {d16} reader
ux = qed.ux.dispatcher(plexus=app, docroot=qed.filesystem.local(root="."), pfs=app.pfs)
# initiate first contact with the sources, the way the server does when it is ready
ux.store.open()
# get the view in the only viewport
view = ux.store._viewports[0].view()
# and the name of the complex pipeline of the fixture
channel = view.pipeline(channel="d16.data.complex").pyre_name
# whose amplitude controller is a range, configured to (-1, -0.5, 0.5, 1)
amplitude = getattr(view.pipeline(channel="d16.data.complex"), "amplitude")
# and whose saturation controller is a value, configured to (0.2, 0.4, 0.6)
saturation = getattr(view.pipeline(channel="d16.data.complex"), "saturation")

# remember the session token
session = view.session
# a drag payload with a consistent extent
_, controller = ux.store.vizUpdateController(
    viewport=0,
    channel=channel,
    name="amplitude",
    configuration={"min": -2.0, "low": -0.75, "high": 0.75, "max": 2.0},
)
# lands both the picks and the extent
assert controller is amplitude
assert (amplitude.min, amplitude.low, amplitude.high, amplitude.max) == (
    -2.0,
    -0.75,
    0.75,
    2.0,
)
# and rolls the session, since the pixels moved
assert view.session != session

# remember the session token
session = view.session
# a drag payload whose extent encroaches on its own picks
ux.store.vizUpdateController(
    viewport=0,
    channel=channel,
    name="amplitude",
    configuration={"min": 0.0, "low": -0.5, "high": 0.5, "max": 2.0},
)
# moves the picks
assert (amplitude.low, amplitude.high) == (-0.5, 0.5)
# but leaves the extent alone
assert (amplitude.min, amplitude.max) == (-2.0, 2.0)
# and still rolls the session
assert view.session != session

# remember the session token
session = view.session
# a hand-set extent that accommodates the picks
_, controller = ux.store.vizResizeController(
    viewport=0, channel=channel, name="amplitude", min=-0.5, max=1.0
)
# moves only the bounds
assert controller is amplitude
assert (amplitude.min, amplitude.low, amplitude.high, amplitude.max) == (
    -0.5,
    -0.5,
    0.5,
    1.0,
)
# leaves the session token alone, since no pixels moved
assert view.session == session
# and pins the controller
assert amplitude.auto is False

# a hand-set extent that encroaches on the picks
try:
    # is refused
    ux.store.vizResizeController(viewport=0, channel=channel, name="amplitude", min=0.0, max=1.0)
# loudly
except journal.ApplicationError:
    # as expected
    pass
# otherwise
else:
    # something is wrong
    assert False, "an encroaching extent was accepted"
# and everything stays put
assert (amplitude.min, amplitude.low, amplitude.high, amplitude.max) == (
    -0.5,
    -0.5,
    0.5,
    1.0,
)
assert view.session == session

# a value controller behaves the same way; an extent that leaves the pick outside
try:
    # is refused
    ux.store.vizResizeController(viewport=0, channel=channel, name="saturation", min=0.5, max=0.6)
# loudly
except journal.ApplicationError:
    # as expected
    pass
# otherwise
else:
    # something is wrong
    assert False, "an extent that excludes the pick was accepted"
# and the controller is untouched
assert (saturation.min, saturation.value, saturation.max) == (0.2, 0.4, 0.6)
# while one that reaches the pick exactly is adopted
_, controller = ux.store.vizResizeController(
    viewport=0, channel=channel, name="saturation", min=0.4, max=1.0
)
assert controller is saturation
assert (saturation.min, saturation.value, saturation.max) == (0.4, 0.4, 1.0)
assert view.session == session

# the hand edits pinned both controllers
assert amplitude.auto is False
assert saturation.auto is False
# releasing one with no statistics on record flips the flag and leaves the bounds alone
_, controller = ux.store.vizSetControllerAuto(
    viewport=0, channel=channel, name="saturation", auto=True
)
assert controller is saturation
assert saturation.auto is True
assert (saturation.min, saturation.value, saturation.max) == (0.4, 0.4, 1.0)
# pinning it again is just as quiet
ux.store.vizSetControllerAuto(viewport=0, channel=channel, name="saturation", auto=False)
assert saturation.auto is False

# seed the accumulated statistics of the dataset on display, the way rendered tiles would
sample = qed.ux.sample()
# with a record that reaches well past the amplitude bounds: count, low, mean, m2, high; the
# amplitude controller works in log scale, so the record is in linear units and its top lands
# on the decade above 4000
sample.merge(record=(1000, 1.0, 100.0, 0.0, 4000.0))
# and file it under the dataset
ux.store._statistics[view.dataset.pyre_name] = sample
# releasing the amplitude controller now catches up with the data right away
_, controller = ux.store.vizSetControllerAuto(
    viewport=0, channel=channel, name="amplitude", auto=True
)
assert controller is amplitude
assert amplitude.auto is True
# the top stretches to the decade above the data, in log scale
assert amplitude.max == 4
# the bottom already accommodates the data, so it stays put
assert amplitude.min == -0.5
# the picks stay put
assert (amplitude.low, amplitude.high) == (-0.5, 0.5)
# and so does the session token, since no pixels moved
assert view.session == session


# end of file
