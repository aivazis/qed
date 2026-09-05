#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that the schema lists the journal channels the server knows about, reads their state
from the live journal, and can turn one on or off
"""

# externals
import types

# support
import journal
import qed

# a stand-in for the journal device the server installs: only its census matters here
device = types.SimpleNamespace(channels={("info", "qed.test.channels.spoken")})
# and for the server that holds it
server = types.SimpleNamespace(journal=device)
# the session resolver hands back the store, and nothing here reads it, so a stand-in will do
store = types.SimpleNamespace()
# the execution context; no application, so the declared channels contribute nothing
context = {"store": store, "server": server}

# the query
listing = """
    query {
        qed {
            journal {
                id
                severity
                name
                active
                fatal
            }
        }
    }
"""
# the mutation
toggle = """
    mutation ($payload: JournalChannelSetInput!) {
        journalChannelSet(input: $payload) {
            channel {
                id
                severity
                name
                active
                fatal
            }
        }
    }
"""


# the session query has to resolve to a store; the schema gets it from the context
def query(document, variables=None):
    """
    Execute {document} against the schema with a store the resolvers accept
    """
    # execute
    result = qed.gql.schema.execute(document, context=context, variables=variables)
    # there must be no errors
    assert not result.errors, result.errors
    # hand back the data
    return result.data


# the listing shows the channel the device has heard, with its live state
channels = query(listing)["qed"]["journal"]
assert channels == [
    {
        "id": "info:qed.test.channels.spoken",
        "severity": "info",
        "name": "qed.test.channels.spoken",
        "active": True,
        "fatal": False,
    }
]

# a debug channel nobody has heard of is off
name = "qed.test.channels.quiet"
assert not journal.debug(name).active
# turn it on
payload = {"severity": "debug", "name": name, "active": True}
channel = query(toggle, variables={"payload": payload})["journalChannelSet"]["channel"]
# the mutation reports the new state
assert channel == {
    "id": f"debug:{name}",
    "severity": "debug",
    "name": name,
    "active": True,
    "fatal": False,
}
# the live channel agrees
assert journal.debug(name).active
# and the channel joined the census, so the listing shows it from now on
channels = query(listing)["qed"]["journal"]
assert [(channel["severity"], channel["name"]) for channel in channels] == [
    ("debug", name),
    ("info", "qed.test.channels.spoken"),
]
# turn it back off
payload["active"] = False
channel = query(toggle, variables={"payload": payload})["journalChannelSet"]["channel"]
assert channel["active"] is False
assert not journal.debug(name).active

# a severity the journal does not have is refused
result = qed.gql.schema.execute(
    toggle, context=context, variables={"payload": {**payload, "severity": "gossip"}}
)
assert result.errors


# end of file
