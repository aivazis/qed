#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a parsed granule id leaves nothing behind: its descriptor is anonymous, so the
configuration store holds nothing on its behalf, and it goes away as soon as its client lets go
of it; a census parses hundreds of thousands of ids, and a descriptor that lingered would cost
memory and slow every later parse down
"""

# externals
import gc
import weakref

# support
import qed

# the parser
registrar = qed.readers.nisar.daac.registrar()
# a granule id
granule = (
    "NISAR_L1_PR_RSLC_005_003_A_028_2005_DHDH_A_20250923T093702_20250923T093738_P00410_N_F_J_001"
)

# parse it
descriptor = registrar.parse(granule)
# the fields are there
assert int(descriptor.cycle) == 5
assert int(descriptor.track) == 3
# but the descriptor has no name
assert descriptor.pyre_name is None

# watch it
watcher = weakref.ref(descriptor)
# let go of it
del descriptor
# and collect
gc.collect()
# it is gone
assert watcher() is None

# and so is every one of a batch
watchers = [weakref.ref(registrar.parse(granule)) for _ in range(100)]
# once collected
gc.collect()
# none of them is left
assert not [watcher for watcher in watchers if watcher() is not None]


# end of file
