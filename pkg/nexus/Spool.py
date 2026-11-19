# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# the channel over the file that holds the payload
from pyre.ipc.File import File


# declaration
class Spool:
    """
    A payload parked in an unlinked temporary file, which travels between processes as a
    channel over the file rather than as its contents

    Workers {stash} their product and return the spool as the result of their task; the
    marshaler carries the channel inside the completion report, and the worker releases its
    own copy once the report is sent. The team side hands out {share}s of the payload, files
    of their own that a response sends straight to the peer, or {view}s of it. The file is
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
        # make a file with no name
        file = File.temporary()
        # deposit the payload
        file.write(bytes=data)
        # and wrap it up
        return cls(size=data.nbytes, file=file)

    # interface - team side
    def share(self):
        """
        Hand out a file of its own over the payload, for a response to send and then close
        """
        # a duplicate of my descriptor outlives me, so the response owns what it sends
        return self.file.share()

    def view(self):
        """
        Map the payload
        """
        # map the spool contents
        return self.file.map(size=self.size)

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
        # the channel over the file that holds the payload
        self.file = file
        # the statistical sample of the rendered source region, when the worker took one
        self.stats = stats
        # all done
        return


# end of file
