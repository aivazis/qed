# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import journal

# support
import qed


# the base profiler
class Profiler(qed.component, family="qed.inspect.profiler"):
    """
    The base profiler
    """

    # interface
    def measure(self):
        """
        Run a profile schedule and report performance
        """
        # send the report to the screen
        self.screen()
        # all done
        return

    # metamethods
    def __init__(self, readers, **kwds):
        # chain up
        super().__init__(**kwds)

        # initialize my pile of datasets
        datasets = {}
        # and my profiling store
        profile = qed.patterns.vivify(levels=2, atom=float)

        # each reader can potentially serve more than one dataset; go through them
        for reader in readers:
            # get the name of the reader
            name = reader.pyre_name
            # access the reader specific timers
            discoveryTimer = qed.timers.wall(f"qed.profiler.discovery.{name}")
            statsTimer = qed.timers.wall(f"qed.profiler.stats.{name}")
            # read the number of milliseconds elapsed while instantiating the reader
            discovery = discoveryTimer.ms()
            # and the number of milliseconds it took to collect statistics
            stats = statsTimer.ms()

            # make a pile of the datasets served by this reader
            available = list(reader.datasets)
            # set up the bookkeeping
            for dataset in available:
                # get the name of this dataset
                name = dataset.pyre_name
                # index the dataset by its name
                datasets[name] = dataset
                # and charge it its portion of the costs
                profile["discovery"][name] = discovery / len(available)
                profile["stats"][name] = stats / len(available)

        # attach my datasets
        self.datasets = datasets
        # and my profiling store
        self.profile = profile

        # all done
        return

    # implementation details
    def screen(self):
        """
        Generate a profiling report to the screen
        """
        # grab my profiling store
        profile = self.profile

        # make a channel
        channel = journal.info("qed.inspect.profiler")
        # sign on
        channel.line(f"profiler:")
        channel.line(f"  number of datasets: {len(self.datasets)}")

        # go through the datasets
        for name in self.datasets:
            # show me the dataset
            channel.line(f"    {name}")
            # and the profiling categories
            for category in self.profile:
                # show me the times
                channel.line(f"      {category}: {profile[category][name]:.3f} ms")

        # flush
        channel.log()

        # all done
        return


# end of file
