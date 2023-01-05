# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# externals
import journal

# support
import qed


# declaration
class Inspect(qed.shells.command, family="qed.cli.inspect"):
    """
    Measure data access performance
    """

    # interface
    @qed.export(tip="measure data access performance")
    def profile(self, plexus, **kwds):
        """
        The main entry point
        """
        # make a profiler
        profiler = qed.inspect.profiler(readers=plexus.datasets)
        # and ask it to do its thing
        profiler.measure()
        # and done
        return 0


# end of file
