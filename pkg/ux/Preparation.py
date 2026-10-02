# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import time


# what has been done to make a dataset worth looking at
class Preparation:
    """
    The record of the work that stands between selecting a dataset and viewing it well

    Selecting a dataset settles what to render; it does not settle how well. The pyramid
    that makes a zoomed out view cheap, the statistics measured over the whole raster rather
    than guessed from a corner, and the thumbnail that reads a level rather than the product
    all come from one pass, and this record is how the client is told whether that pass has
    happened yet
    """

    # constants
    # the states the work can be in
    working = "working"
    seeded = "seeded"
    ready = "ready"
    failed = "failed"

    # interface
    def seed(self):
        """
        Mark the work as far enough along to render by: the first tiles of the pyramid,
        the ones spread over the extent the way the probe samples it, have reported, so
        the statistics are an estimate rather than a guess, and the levels keep building
        while the view shows the product at full resolution
        """
        # a preparation that is over has nothing to seed
        if self.status != self.working:
            # so leave it alone
            return self
        # otherwise, mark it
        self.status = self.seeded
        # and note when
        self.sown = time.time()
        # all done
        return self

    def succeed(self):
        """
        Mark the work as done
        """
        # the dataset is worth looking at
        self.status = self.ready
        # nothing went wrong
        self.error = None
        # stop the clock
        self._stop()
        # all done
        return self

    def fail(self, error):
        """
        Mark the work as failed, retaining {error} as the reason
        """
        # the dataset is viewable, just not as well as it might have been
        self.status = self.failed
        # and this is why; keep the text, since the client displays it
        self.error = str(error)
        # stop the clock
        self._stop()
        # all done
        return self

    # metamethods
    def describe(self) -> dict:
        """
        Describe the state of the work: its status and times, the depth of the pyramid of the
        dataset and how much of it is available, and the build of each raster behind it

        A dataset is read at one depth with the rasters that accompany it, so its depth and
        its reach are the smallest among its rasters
        """
        # describe the builds
        rasters = [build.describe() for build in self.builds]
        # assemble the description
        return {
            "dataset": self.name,
            "status": self.status,
            "error": self.error,
            "started": self.started,
            "seeded": self.sown,
            "finished": self.finished,
            "depth": min((raster["depth"] for raster in rasters), default=0),
            "reach": min((raster["reach"] for raster in rasters), default=0),
            "rasters": rasters,
        }

    def __init__(self, name: str | None = None, **kwds):
        # chain up
        super().__init__(**kwds)
        # the dataset the work is for
        self.name = name
        # the work begins the moment the record is opened
        self.status = self.working
        # with nothing to report
        self.error = None
        # and no measured attempt
        self.elapsed = None
        # the builds behind the work, one for each raster, attached by whoever starts them
        self.builds = []
        # when the work started, when it was seeded, and when it finished
        self.started = time.time()
        self.sown = None
        self.finished = None
        # start the clock
        self._started = self.started
        # all done
        return

    # implementation details
    def _stop(self):
        """
        Record how long the work took
        """
        # if the clock was started
        if self._started is not None:
            # note when the work finished
            self.finished = time.time()
            # measure the attempt
            self.elapsed = self.finished - self._started
            # and idle the clock
            self._started = None
        # all done
        return self


# end of file
