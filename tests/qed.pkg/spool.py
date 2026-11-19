#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that spooled payloads survive their trip: stashed, carried inside a message over a
channel, mapped on arrival, and shared with a response that outlives the spool
"""

# externals
import os

# support
import pyre
import qed

# a recognizable payload
payload = bytes(range(256)) * 16

# stash it
spool = qed.nexus.spool.stash(data=payload)
# the spool knows its extent
assert spool.size == len(payload)
# and holds the payload
assert spool.file is not None

# the channel the message travels over, the way a crew member reports to its team
parent, child = pyre.ipc.newSocket().open()
# and the marshaler
marshaler = pyre.ipc.newPickler()
# the worker side sends the spool inside a message
manifest = marshaler.send(item=spool, channel=child)
# which carries the file the spool holds
assert manifest.channels == [spool.file]
# the worker releases its copy; the kernel keeps the payload alive for the recipient
spool.close()

# the team side receives the message
clone = marshaler.recv(channel=parent)
# the spool arrives whole
assert clone.size == len(payload)
# with a file of its own
assert clone.file is not None

# map the payload
view = clone.view()
# which survives the round trip
assert bytes(view) == payload
# release the mapping
view.close()

# a share is a file of its own over the payload
share = clone.share()
# which holds the payload
assert os.pread(share.fileno(), clone.size, 0) == payload
# and outlives the spool, the way a response outlives the eviction of its tile from the cache
clone.close()
# so it still holds the payload
assert os.pread(share.fileno(), len(payload), 0) == payload
# until the response lets it go
share.close()

# clean up
parent.close()
# both ends
child.close()


# end of file
