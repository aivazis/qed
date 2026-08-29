# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import time


# where a data source stands on its way to being viewable
class Lifecycle:
    """
    The staging record of a single data source

    A source is {connected} the moment the server learns of it, {staging} while its crew
    surveys the product, and then either {ready} or {failed}; a failure retains its reason,
    so the client can show it and offer a retry instead of dropping the source silently
    """

    # constants
    # the states a source can be in
    connected = "connected"
    staging = "staging"
    ready = "ready"
    failed = "failed"

    # interface
    def begin(self):
        """
        Mark the beginning of first contact
        """
        # the survey is under way
        self.status = self.staging
        # a fresh attempt carries no error
        self.error = None
        # start the clock
        self._started = time.time()
        # and forget whatever the previous attempt took
        self.elapsed = None
        # all done
        return self

    def succeed(self):
        """
        Mark the arrival of a complete discovery record
        """
        # the source is viewable
        self.status = self.ready
        # nothing went wrong
        self.error = None
        # stop the clock
        self._stop()
        # all done
        return self

    def fail(self, error):
        """
        Mark first contact as failed, retaining {error} as the reason
        """
        # the source is not viewable
        self.status = self.failed
        # and this is why; keep the text, since the client displays it
        self.error = str(error)
        # stop the clock
        self._stop()
        # all done
        return self

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # a source starts out known but untouched
        self.status = self.connected
        # with nothing to report
        self.error = None
        # and no measured attempt
        self.elapsed = None
        # the clock is idle
        self._started = None
        # all done
        return

    # implementation details
    def _stop(self):
        """
        Record how long the attempt took
        """
        # if the clock was started
        if self._started is not None:
            # measure the attempt
            self.elapsed = time.time() - self._started
            # and idle the clock
            self._started = None
        # all done
        return self


# end of file
