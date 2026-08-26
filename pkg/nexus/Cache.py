# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import collections

# support
import qed
import journal


# the tile cache
class Cache(qed.component, family="qed.nexus.caches.tile"):
    """
    A cache of rendered tiles, keyed by the full request specification

    Entries are the spools the workers rendered into: unlinked files whose storage the kernel
    reclaims the moment the last descriptor closes. The cache owns every spool handed to it,
    and closes the ones it evicts; readers map their own views, which survive eviction. Tasks
    carry their complete specification as their identity, controller state included, so a hit
    is guaranteed to be pixel-identical to a fresh render
    """

    # user configurable state
    capacity = qed.properties.int(default=128 * 1024 * 1024)
    capacity.doc = "the total payload size to hold, in bytes; zero disables the cache"

    # interface
    def lookup(self, task):
        """
        Retrieve the spool that holds the render of {task}, if it is on hand
        """
        # look it up
        spool = self.entries.get(task)
        # if it is not here
        if spool is None:
            # count the miss
            self.misses += 1
            # and report the bad news
            return None
        # otherwise, refresh its place in the eviction order
        self.entries.move_to_end(task)
        # count the hit
        self.hits += 1
        # tell me
        channel = journal.debug("qed.nexus.cache")
        # what happened
        channel.log(f"hit: {self.hits} hits, {self.misses} misses")
        # and hand off the spool
        return spool

    def insert(self, task, spool):
        """
        Take ownership of the {spool} that holds the render of {task}
        """
        # a trivial capacity disables the cache
        if self.capacity <= 0:
            # so release the spool immediately
            spool.close()
            # and bail
            return self
        # if an older render of the same specification is on hand, e.g. after an eviction
        # raced a re-render
        stale = self.entries.pop(task, None)
        # release it
        if stale is not None:
            # and adjust the books
            self.held -= stale.size
            stale.close()
        # admit the new entry
        self.entries[task] = spool
        # and adjust the books
        self.held += spool.size
        # while the budget is exceeded
        while self.held > self.capacity and self.entries:
            # evict the least recently used entry
            victim, evicted = self.entries.popitem(last=False)
            # adjust the books
            self.held -= evicted.size
            # and release its payload
            evicted.close()
        # all done
        return self

    def purge(self, reader):
        """
        Drop every entry rendered from {reader}, e.g. because it was disconnected
        """
        # go through a snapshot of the entries
        for task in [task for task in self.entries if task.reader == reader]:
            # remove each match
            spool = self.entries.pop(task)
            # adjust the books
            self.held -= spool.size
            # and release its payload
            spool.close()
        # all done
        return self

    def clear(self):
        """
        Release every entry
        """
        # go through the entries
        for spool in self.entries.values():
            # and release each payload
            spool.close()
        # empty the table
        self.entries.clear()
        # and reset the books
        self.held = 0
        # all done
        return self

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the table of spools, keyed by their task, in eviction order
        self.entries = collections.OrderedDict()
        # the total payload size on hand
        self.held = 0
        # the service statistics
        self.hits = 0
        self.misses = 0
        # all done
        return


# end of file
