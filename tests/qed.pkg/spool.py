#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that spooled payloads survive their trip: stashed, pickled as a stub, their descriptor
shipped over a channel, adopted, mapped, and shared with a response that outlives the spool
"""

# externals
import os
import pickle

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

# the wire form carries only the size, never the descriptor
clone = pickle.loads(pickle.dumps(spool))
assert clone.size == spool.size
assert clone.file is None

# ship the descriptor over a channel, the way a crew member does with its report
parent, child = pyre.ipc.newSocket().open()
# the worker side sends it
child.sendDescriptors(descriptors=[spool.file.fileno()])
# and releases its copy; the kernel keeps the payload alive for the recipient
spool.close()

# the team side receives it
_, descriptors = parent.recvDescriptors(limit=1)
# exactly one made the trip
assert len(descriptors) == 1
# attach it to the stub that came off the wire
clone.adopt(descriptor=descriptors[0])

# the payload survives the round trip
view = clone.view()
assert bytes(view) == payload
# release the mapping
view.close()

# a share is a file of its own over the payload
share = clone.share()
# which holds the payload
assert os.pread(share.fileno(), clone.size, 0) == payload
# and outlives the spool, the way a response outlives the eviction of its tile from the cache
clone.close()
assert os.pread(share.fileno(), len(payload), 0) == payload
# until the response lets it go
share.close()


# end of file
