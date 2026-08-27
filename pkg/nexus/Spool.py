# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import mmap
import os
import tempfile


# the parking place for rendered payloads
class Spool:
    """
    A payload parked in an unlinked temporary file whose descriptor, rather than its contents,
    travels between processes

    Workers {stash} their product and ship the spool with their completion report: the pickled
    part is just the size, and the descriptor follows as ancillary data on the crew channel.
    The team side {adopt}s the descriptor and hands out {view}s of the payload. The file is
    unlinked from birth, so the kernel reclaims the storage when the last descriptor closes,
    no matter how either process exits
    """

    # interface - worker side
    @classmethod
    def stash(cls, data):
        """
        Park {data} in a fresh spool
        """
        # normalize the payload so its true extent is known
        data = memoryview(data)
        # make an unlinked temporary file
        file = tempfile.TemporaryFile()
        # deposit the payload
        file.write(data)
        # and push it out so the descriptor can travel
        file.flush()
        # wrap it up
        return cls(size=data.nbytes, file=file)

    # interface - team side
    def adopt(self, descriptor):
        """
        Attach the payload {descriptor} that arrived over the wire
        """
        # dress it up as a file
        self.file = os.fdopen(descriptor, "rb")
        # all done
        return self

    def view(self):
        """
        Map the payload
        """
        # map the spool contents; the file position the descriptor arrived with is irrelevant
        return mmap.mmap(self.file.fileno(), self.size, access=mmap.ACCESS_READ)

    def close(self):
        """
        Release my hold on the payload
        """
        # if my file is still attached
        if self.file is not None:
            # close it
            self.file.close()
            # and forget it
            self.file = None
        # all done
        return

    # metamethods
    def __init__(self, size, file=None, stats=None, **kwds):
        # chain up
        super().__init__(**kwds)
        # the payload size
        self.size = size
        # the file that holds the payload
        self.file = file
        # the statistical sample of the rendered source region, when the worker took one
        self.stats = stats
        # all done
        return

    def __getstate__(self):
        """
        Prepare for the trip over the wire
        """
        # descriptors cannot travel in the byte stream; the size and the statistics record,
        # a small tuple of floats, are the only pickled cargo
        return {"size": self.size, "stats": self.stats}

    def __setstate__(self, state):
        """
        Arrive from the wire
        """
        # restore the size
        self.size = state["size"]
        # and the statistics record, tolerating reports from workers that took no sample
        self.stats = state.get("stats")
        # the descriptor arrives separately, as ancillary data
        self.file = None
        # all done
        return


# end of file
