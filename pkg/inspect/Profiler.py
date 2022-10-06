# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import csv
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
        profile = qed.patterns.vivify(levels=3, atom=float)
        # and a timer
        tileTimer = qed.timers.wall("qed.profiler.tiles")

        # go through the datasets
        for dataset, discovery, stats in self.datasets():
            # get the name of the dataset
            name = dataset.pyre_name
            # save the startup costs
            profile[name]["startup"]["discovery"] = discovery
            profile[name]["startup"]["stats"] = stats
            # go through its channels
            for channel in dataset.channels:
                # make tile exponents
                for tileExp in range(5, 13):
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
                        profile[name]["tiles"][channel, tile, zoom] = tileTimer.ms()
                        # reset the timer
                        tileTimer.reset()

        # send the report to the screen
        self.screen(profile=profile)
        # and save a csv file
        self.csv(profile=profile)
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
                yield dataset, discovery, stats

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
        for name, phases in profile.items():
            # show me the dataset
            channel.line(f"    {name}")
            # go through the phases
            for times in phases.values():
                # and the profiling categories
                for category, cost in times.items():
                    # show me the times
                    channel.line(f"      {category}: {cost:.3f} ms")
        # flush
        channel.log()

        # all done
        return

    def csv(self, profile):
        """
        Save the {profile} as a {csv} file
        """
        # make a pile of all shapes
        shapes = set()
        # a pile of all channels
        channels = set()
        # and a new table
        table = qed.patterns.vivify(levels=3, atom=type(None))

        # go through the datasets
        for name in profile:
            # and the tile timings for each one
            for (channel, shape, _), cost in profile[name]["tiles"].items():
                # record the shape
                shapes.add(shape)
                # the channel
                channels.add(channel)
                # and the cost
                table[shape][channel][name] = cost

        # write string scaling data out to a CSV file
        with open("qed-strong.csv", mode="w", newline="") as stream:
            # make a writer
            writer = csv.writer(stream)
            # build my headers
            headers = ["tile", "pixels"] + [
                f"{name}.{channel}" for name in profile for channel in sorted(channels)
            ]
            writer.writerow(headers)

            # go through the shapes
            for shape in sorted(shapes):
                # compute the number of pixels
                pixels = shape[0] * shape[1]
                # build the record
                record = [shape, pixels] + [
                    (
                        profile[name]["startup"]["discovery"]
                        + table[shape][channel][name]
                    )
                    if table[shape][channel][name] is not None
                    else None
                    for name in profile
                    for channel in sorted(channels)
                ]
                writer.writerow(record)

        # write weak scaling data out to a CSV file
        with open("qed-weak.csv", mode="w", newline="") as stream:
            # make a writer
            writer = csv.writer(stream)
            # build my headers
            headers = ["tile", "pixels"] + [
                f"{name}.{channel}" for name in profile for channel in sorted(channels)
            ]
            writer.writerow(headers)

            # go through the shapes
            for shape in sorted(shapes):
                # compute the number of pixels
                pixels = shape[0] * shape[1]
                # build the record
                record = [shape, pixels] + [
                    (
                        profile[name]["startup"]["discovery"]
                        + table[shape][channel][name]
                    )
                    / pixels
                    if table[shape][channel][name] is not None
                    else None
                    for name in profile
                    for channel in sorted(channels)
                ]
                writer.writerow(record)

        # all done
        return


# end of file
