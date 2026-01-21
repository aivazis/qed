#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed


# the driver
class Fetch(qed.application, family="qed.apps.perf.fetch"):
    """
    Measure tile creation performance
    """

    # interface
    @qed.export
    def main(self, *args, **kwds):
        """
        The main entry point
        """
        # all done
        return 0


# bootstrap
if __name__ == "__main__":
    # instantiate
    app = Fetch(name="fetch")
    # invoke the driver
    status = app.run()
    # and share the status with the shell
    raise SystemExit(status)


# end of file
