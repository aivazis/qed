#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the journal device mirrors every entry, keeps a bounded history, lifts the origin of
replayed entries into the envelope, publishes batches on the journal topic, and stays out of
its own way when the hub speaks up
"""

# externals
import json
import os

# support
import pyre
import journal
import qed

# the stream framing the device uses
from pyre.http.EventStream import EventStream

# the unit of time
from pyre.units.SI import second


# a capturing device, for the mirror
class Capture(journal.device):
    """
    A device that remembers every entry it is handed
    """

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(name="capture", **kwds)
        # nothing recorded yet
        self.calls = []
        # all done
        return

    # interface
    def alert(self, entry):
        # a user-facing alert
        self.calls.append(("alert", list(entry.page)))
        # all done
        return self

    def memo(self, entry):
        # a developer-facing memo
        self.calls.append(("memo", list(entry.page)))
        # all done
        return self

    def help(self, entry):
        # a help screen
        self.calls.append(("help", list(entry.page)))
        # all done
        return self


# a stand-in for the hub that records what it is asked to publish
class Hub:
    """
    The minimal hub surface the device needs
    """

    # metamethods
    def __init__(self, chatty=False):
        # what was published
        self.published = []
        # whether publishing provokes an entry
        self.chatty = chatty
        # all done
        return

    # interface
    def publish(self, event, topic="", coalesce=False):
        # record
        self.published.append((event, topic, coalesce))
        # if i am the kind that complains while working
        if self.chatty:
            # do so
            journal.warning("test.console.hub").log("a slow client")
        # all done
        return


# a stand-in for the server
class Server:
    """
    The pieces of a server the device consults
    """

    # the identification string responses stamp into their headers
    name = "qed/test"
    # the stream framing
    eventStream = EventStream

    # metamethods
    def __init__(self, chatty=False):
        # an event loop, for the alarm
        self.dispatcher = pyre.ipc.newPSL()
        # and a hub
        self.hub = Hub(chatty=chatty)
        # all done
        return


# decode the payload of a frame
def unpack(frame):
    """
    Check the framing of {frame} and hand back the records it carries
    """
    # the frame is named
    assert frame.startswith(b"event: journal\ndata: ")
    # and terminated
    assert frame.endswith(b"\n\n")
    # the payload is the data line
    data = frame[len(b"event: journal\ndata: ") : -2]
    # a list of wire objects
    return json.loads(data)


# the channel name
name = "test.console"

# the server pieces
server = Server()
# a mirror
mirror = Capture()
# the device, with a short history and a short latency
device = qed.ux.journal(server=server, mirror=mirror, capacity=4, latency=0.05 * second)
# check its name
assert device.name == "journal"
# install it
journal.chronicler.device = device

# log through three sinks
journal.info(name).log("one")
journal.warning(name).log("two")
debug = journal.debug(name)
debug.active = True
debug.log("three")
# the mirror saw all three, in order
assert mirror.calls == [("alert", ["one"]), ("alert", ["two"]), ("memo", ["three"])]
# the history has them
assert [record.page for record in device.history] == [["one"], ["two"], ["three"]]
# stamped by me
assert all(record.pid == os.getpid() for record in device.history)
assert [record.seq for record in device.history] == [1, 2, 3]
# the channels were noted
assert device.channels == {("info", name), ("warning", name), ("debug", name)}
# they are waiting to go out
assert len(device.pending) == 3
assert device.armed
# and nothing has gone out yet
assert server.hub.published == []

# let the loop run until the alarm fires
server.dispatcher.watch()
# one frame went out, on the journal topic, uncoalesced
assert len(server.hub.published) == 1
frame, topic, coalesce = server.hub.published[0]
assert topic == "journal"
assert coalesce is False
# carrying the three records
records = unpack(frame)
assert [record["page"] for record in records] == [["one"], ["two"], ["three"]]
assert [record["seq"] for record in records] == [1, 2, 3]
assert records[0]["sink"] == "alert"
assert records[2]["sink"] == "memo"
assert records[0]["notes"]["channel"] == name
# the queue is empty and the alarm is spent
assert device.pending == []
assert not device.armed

# a record from a crew member, replayed the way the nexus does it
foreign = journal.record(
    sink="alert",
    page=["from a worker"],
    notes={"channel": name, "severity": "info", "application": "qed"},
    seq=5,
    pid=99,
    time=12.5,
)
journal.replay(record=foreign)
# it is in the history, with the origin lifted into the envelope
record = device.history[-1]
assert record.page == ["from a worker"]
assert record.pid == 99
assert record.seq == 5
assert record.time == 12.5
# and the notes as the worker flushed them, without the copies
assert record.notes == {"channel": name, "severity": "info", "application": "qed"}
# my own sequence did not move
assert device.seq == 3

# a user note that happens to be named like an origin field is left alone
journal.info(name).log("mine", pid="not a number", seq="x", time="now")
record = device.history[-1]
assert record.pid == os.getpid()
assert record.seq == 4
assert record.notes["pid"] == "not a number"

# the history is bounded
journal.info(name).log("five")
journal.info(name).log("six")
assert len(device.history) == 4
assert device.history[0].page == ["from a worker"]
assert device.history[-1].page == ["six"]
# and a newcomer is opened with all of it
assert [record["page"] for record in unpack(device.opening())] == [
    ["from a worker"],
    ["mine"],
    ["five"],
    ["six"],
]
# drain the queue
server.dispatcher.watch()
assert len(server.hub.published) == 2

# a hub that speaks up while publishing does not loop back into the queue
server = Server(chatty=True)
device = qed.ux.journal(server=server, mirror=mirror, capacity=4, latency=0.05 * second)
journal.chronicler.device = device
# log something
journal.info(name).log("provoke")
# let the loop run until the batch goes out
server.dispatcher.watch()
# the hub published once
assert len(server.hub.published) == 1
# its complaint was recorded
assert device.history[-1].channel == "test.console.hub"
assert device.history[-1].page == ["a slow client"]
# but not queued, so nothing is armed and the loop had nothing more to do
assert device.pending == []
assert not device.armed
assert not device.publishing
# a newcomer, though, is shown the complaint
assert len(unpack(device.opening())) == 2

# give the journal back to the mirror
journal.chronicler.device = mirror


# end of file
