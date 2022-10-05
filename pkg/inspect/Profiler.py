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
        # make a channel
        c = journal.info("qed.inspect.profile")
        # a profiling store
        profile = qed.patterns.vivify(levels=2, atom=float)
        # and a timer
        tileTimer = qed.timers.wall("qed.profiler.tiles")

        # go through the datasets
        for dataset, discovery, stats in self.datasets():
            # get the name of the dataset
            name = dataset.pyre_name
            # save the startup costs
            profile[name]["discovery"] = discovery
            profile[name]["stats"] = stats
            # go through its channels
            for channel in dataset.channels:
                # make tile exponents
                for tileExp in range(5, 11):
                    # make a tile
                    tile = (2**tileExp,) * 2
                    # make zoom
                    for zoom in range(1):
                        # show me
                        c.log(f"measuring {name}, {channel}, {tile}")
                        # start the timer
                        tileTimer.start()
                        # attempt to
                        try:
                            # render a tile
                            dataset.render(
                                channel=channel, zoom=zoom, origin=(0, 0), shape=tile
                            )
                        # if anything goes wrong
                        except qed.exceptions.PyreError:
                            # ignore and move on
                            continue
                        # stop the timer
                        tileTimer.stop()
                        # record the time
                        profile[name][channel, tile, zoom] = tileTimer.ms()
                        # reset the timer
                        tileTimer.reset()

        # send the report to the screen
        self.screen(profile=profile)
        # all done
        return

    # metamethods
    def __init__(self, readers, **kwds):
        # chain up
        super().__init__(**kwds)
        # save the readers
        self.readers = readers
        # all done
        return

    # implementation details
    def datasets(self):
        """
        Ask all {readers} for their dataset
        """
        # go through my readers
        for reader in self.readers:
            # get the name of the reader
            name = reader.pyre_name
            # find out how many datasets it knows about
            available = len(reader.datasets)

            # access the reader specific timers
            discoveryTimer = qed.timers.wall(f"qed.profiler.discovery.{name}")
            statsTimer = qed.timers.wall(f"qed.profiler.stats.{name}")
            # read the number of milliseconds elapsed while instantiating the reader
            discovery = discoveryTimer.ms()
            # and the number of milliseconds it took to collect statistics
            stats = statsTimer.ms()

            # go through each dataset
            for dataset in reader.datasets:
                # and report it along with the access times
                yield dataset, discovery / available, stats / available

        # all done
        return

    def screen(self, profile):
        """
        Generate a profiling report to the screen
        """
        # make a channel
        channel = journal.info("qed.inspect.profiler")
        # sign on
        channel.line(f"profiler:")
        channel.line(f"  number of datasets: {len(profile)}")

        # go through the datasets
        for name, times in profile.items():
            # show me the dataset
            channel.line(f"    {name}")
            # and the profiling categories
            for category, cost in times.items():
                # show me the times
                channel.line(f"      {category}: {cost:.3f} ms")

        # flush
        channel.log()

        # all done
        return


# end of file
