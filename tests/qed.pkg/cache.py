#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check the tile cache: lookups, least-recently-used eviction under a byte budget, purging by
data source, and the ownership of evicted payloads
"""

# externals
import types

# support
import qed


# a stand-in task with a controllable identity
class Probe:
    """
    A hashable request specification with a nominal reader
    """

    # metamethods
    def __init__(self, tag, reader="source", **kwds):
        # chain up
        super().__init__(**kwds)
        # save my identity
        self.tag = tag
        self.reader = reader
        # all done
        return

    def __hash__(self):
        # my identity is my tag
        return hash(self.tag)

    def __eq__(self, other):
        # two probes with the same tag are the same work
        return type(other) is type(self) and other.tag == self.tag


# a payload factory
def payload(size):
    """
    Park {size} bytes in a spool
    """
    # easy enough
    return qed.nexus.spool.stash(data=bytes(size))


# build a cache with room for three 100-byte payloads
cache = qed.nexus.cache(name="qed.test.cache")
cache.capacity = 300

# a miss on an empty cache
assert cache.lookup(task=Probe(tag="a")) is None
assert cache.misses == 1

# insert three entries, filling the budget exactly
a, b, c = Probe(tag="a"), Probe(tag="b"), Probe(tag="c")
for probe in (a, b, c):
    cache.insert(task=probe, spool=payload(size=100))
assert cache.held == 300

# all three are hits
assert cache.lookup(task=a) is not None
assert cache.lookup(task=b) is not None
assert cache.lookup(task=c) is not None
assert cache.hits == 3

# touch {a} so {b} becomes the least recently used
cache.lookup(task=a)
# a fourth entry exceeds the budget and evicts {b}
d = Probe(tag="d")
cache.insert(task=d, spool=payload(size=100))
assert cache.held == 300
# {b} is gone
missing = b not in cache.entries
assert missing
# and the others survived
assert all(probe in cache.entries for probe in (a, c, d))

# eviction released the payload; a fresh insert-then-evict pair makes that observable
big = payload(size=250)
cache.insert(task=Probe(tag="big"), spool=big)
# the big entry evicted the older ones but fits itself
assert cache.held <= 300
# push it out with another entry
overflow = payload(size=200)
cache.insert(task=Probe(tag="overflow"), spool=overflow)
# the big spool was closed on its way out
assert big.file is None
# while the resident one is open
assert overflow.file is not None

# purge by data source: entries from a different reader survive
cache.clear()
cache.insert(task=Probe(tag="x", reader="one"), spool=payload(size=10))
cache.insert(task=Probe(tag="y", reader="two"), spool=payload(size=10))
cache.purge(reader="one")
assert Probe(tag="x") not in cache.entries
assert Probe(tag="y") in cache.entries
assert cache.held == 10

# a zero capacity disables the cache: the spool is released on arrival
cache.clear()
cache.capacity = 0
declined = payload(size=10)
cache.insert(task=Probe(tag="z"), spool=declined)
assert declined.file is None
assert len(cache.entries) == 0


# end of file
