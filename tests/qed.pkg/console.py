#!/usr/bin/env python3
# -*- python -*-
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
import socket

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
        # the change notifications sent
        self.notifications = 0
        # all done
        return

    # interface
    def notifyChange(self):
        # count
        self.notifications += 1
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
# a warning
journal.warning(name).log("two")
# and a debug channel
debug = journal.debug(name)
debug.active = True
# that is turned on
debug.log("three")
# the mirror saw all three, in order
assert mirror.calls == [("alert", ["one"]), ("alert", ["two"]), ("memo", ["three"])]
# the history has them
assert [record.page for record in device.history] == [["one"], ["two"], ["three"]]
# stamped by me: the origin is in the notes
assert all(record.notes["pid"] == str(os.getpid()) for record in device.history)
# the host
assert all(record.notes["host"] == socket.gethostname() for record in device.history)
# the time
assert all(float(record.notes["time"]) > 0 for record in device.history)
# and the sequence of my entries
assert [record.notes["seq"] for record in device.history] == ["1", "2", "3"]
# and each one was counted on arrival
assert [record.notes["serial"] for record in device.history] == ["1", "2", "3"]
# the channels were noted
assert device.channels == {("info", name), ("warning", name), ("debug", name)}
# and every first-time speaker was news to the clients
assert server.notifications == 3
# they are waiting to go out
assert len(device.pending) == 3
# with the alarm set
assert device.armed
# and nothing has gone out yet
assert server.hub.published == []

# let the loop run until the alarm fires
server.dispatcher.watch()
# one frame went out, on the journal topic, uncoalesced
assert len(server.hub.published) == 1
# unpack it
frame, topic, coalesce = server.hub.published[0]
# on the journal topic
assert topic == "journal"
# uncoalesced
assert coalesce is False
# carrying the three records, as page and notes
records = unpack(frame)
# in order
assert [record["page"] for record in records] == [["one"], ["two"], ["three"]]
# with their sequence
assert [record["notes"]["seq"] for record in records] == ["1", "2", "3"]
# and the serials a client uses to tell what it already holds
assert [record["notes"]["serial"] for record in records] == ["1", "2", "3"]
# the first at the info severity
assert records[0]["notes"]["severity"] == "info"
# and the last at the debug severity
assert records[2]["notes"]["severity"] == "debug"
# with the name of the channel
assert records[0]["notes"]["channel"] == name
# and the records hold nothing else
assert set(records[0]) == {"journal", "page", "notes"}
# the queue is empty and the alarm is spent
assert device.pending == []
# and the alarm is spent
assert not device.armed
# a channel that speaks again is not news
journal.info(name).log("one more")
# so the count did not move
assert server.notifications == 3

# a record from a crew member, replayed the way the nexus does it, with the origin its
# courier stamped
stamped = {
    "channel": name,
    "severity": "info",
    "application": "qed",
    "pid": "99",
    "seq": "5",
    "time": "12.5",
    "host": "afar",
}
# replay it here
journal.replay(record=journal.record(page=["from a worker"], notes=stamped))
# it is in the history, with the origin exactly as the worker's courier shipped it, and the
# serial of the fifth arrival at this device, which no worker could have known
record = device.history[-1]
# with its page
assert record.page == ["from a worker"]
# and the notes the worker shipped, along with its serial
assert record.notes == {**stamped, "serial": "5"}
# my own sequence did not move past the four entries of my own
assert device.seq == 4

# an entry that says where it came from but not when is filled in, not overwritten
journal.info(name).log("mine", pid="77", seq="9")
# the last entry
record = device.history[-1]
# keeps the origin it said
assert record.notes["pid"] == "77"
# and its sequence
assert record.notes["seq"] == "9"
# while the time
assert float(record.notes["time"]) > 0
# and the host are filled in
assert record.notes["host"] == socket.gethostname()
# and my own sequence still did not move
assert device.seq == 4

# the history is bounded
journal.info(name).log("five")
# and another one
journal.info(name).log("six")
# so the history holds the last four
assert len(device.history) == 4
# starting with the entry of the worker
assert device.history[0].page == ["from a worker"]
# and ending with the last one
assert device.history[-1].page == ["six"]
# which is the sixth of mine
assert device.history[-1].notes["seq"] == "6"
# and a newcomer is opened with all of it
assert [record["page"] for record in unpack(device.opening())] == [
    ["from a worker"],
    ["mine"],
    ["five"],
    ["six"],
]
# the serials count arrivals from anywhere without a gap, so a client that was sent some of
# these already can tell which ones, even though the sequence numbers of the origins repeat
assert [record["notes"]["serial"] for record in unpack(device.opening())] == ["5", "6", "7", "8"]
# drain the queue
server.dispatcher.watch()
# so the second frame went out
assert len(server.hub.published) == 2

# a hub that speaks up while publishing does not loop back into the queue
server = Server(chatty=True)
# and a device over it
device = qed.ux.journal(server=server, mirror=mirror, capacity=4, latency=0.05 * second)
# which takes over the journal
journal.chronicler.device = device
# log something
journal.info(name).log("provoke")
# let the loop run until the batch goes out
server.dispatcher.watch()
# the hub published once
assert len(server.hub.published) == 1
# its complaint was recorded
assert device.history[-1].channel == "test.console.hub"
# with its page
assert device.history[-1].page == ["a slow client"]
# but not queued, so nothing is armed and the loop had nothing more to do
assert device.pending == []
# the alarm is not set
assert not device.armed
# and the device is not publishing
assert not device.publishing
# a newcomer, though, is shown the complaint
assert len(unpack(device.opening())) == 2

# give the journal back to the mirror
journal.chronicler.device = mirror


# end of file
