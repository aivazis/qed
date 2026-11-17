#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the app puts the journal channels it owns under the control of its users, each one
exactly once, so the switch in the configuration of this directory reaches its channel
"""

# support
import journal
import qed

# load the app, so the configuration in this directory is processed
app = qed.shells.qed(name="qed.app")
# get the channels it puts under the control of its users
channels = list(app.pyre_journalChannels())
# the complaint about an installation with no web client is among them
assert ("warning", "qed.startup.assets") in channels
# and none appears twice
assert len(channels) == len(set(channels))
# the configuration of this directory switched it off
assert journal.warning("qed.startup.assets").active is False


# end of file
