# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


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

    # configurable state
    channels = qed.properties.strings()
    channels.default = ["complex"]
    channels.doc = "the channels to use during profiling"

    tiles = qed.properties.tuple(schema=qed.properties.int())
    tiles.default = 5, 14
    tiles.doc = "the range of exponents used to make tile shapes"

    zoom = qed.properties.tuple(schema=qed.properties.int())
    zoom.default = 0, 1
    zoom.doc = "the sequence of zoom levels"

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

        # build the target tiles
        tiles = [(2**pow,) * 2 for pow in range(*self.tiles)]
        # and the target zoon levels
        zoomLevels = tuple(range(*self.zoom))
        # go through the datasets
        for dataset, discovery, stats in self.datasets():
            # get the name of the dataset
            name = dataset.pyre_name
            # save the startup costs
            profile[name]["startup"]["discovery"] = discovery
            profile[name]["startup"]["stats"] = stats
            # go through its channels
            for channel in self.channels:
                # make tile exponents
                for tile in tiles:
                    # make zoom
                    for zoom in zoomLevels:
                        # show me
                        c.log(f"measuring {name}, {channel}, {tile}")
                        # reset the timer
                        tileTimer.reset()
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
                            # stop the timer
                            tileTimer.stop()
                            # leave a marker
                            profile[name]["tiles"][channel, tile, zoom] = ""
                            # and move on
                            continue
                        # if all goes well, stop the timer
                        tileTimer.stop()
                        # and record the time
                        profile[name]["tiles"][channel, tile, zoom] = tileTimer.ms()

        # send the report to the screen
        # self.screen(profile=profile)
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
            # and the number of available datasets
            available = len(reader.datasets)

            # access the reader specific timers
            discoveryTimer = qed.timers.wall(f"qed.profiler.discovery.{name}")
            statsTimer = qed.timers.wall(f"qed.profiler.stats.{name}")
            # read the number of milliseconds elapsed while instantiating the reader
            discovery = discoveryTimer.ms()
            # and the number of milliseconds it took to collect statistics
            # split over the number of available datasets
            stats = statsTimer.ms() / available

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
        # get the channels
        channels = self.channels
        # build the target tiles
        tiles = [(2**pow,) * 2 for pow in range(*self.tiles)]
        # and the target zoom levels
        zoomLevels = tuple(range(*self.zoom))

        # save the profile data
        with open(f"{self.pyre_host.nickname}.csv", mode="w", newline="") as stream:
            # make a writer
            writer = csv.writer(stream)
            # the first row of headers has the tiles shapes
            headers = [""] + tiles
            # write it out
            writer.writerow(headers)
            # the second row of headers expands out the number of pixels in each tile
            headers = ["dataset"] + [x * y for x, y in tiles]
            # write it out
            writer.writerow(headers)

            # go through the datasets
            for name in profile:
                # the zoom levels
                for zoom in zoomLevels:
                    # the channels
                    for channel in channels:
                        # assemble the record
                        record = [f"{name}.{channel}"] + [
                            profile[name]["tiles"][channel, shape, zoom]
                            for shape in tiles
                        ]
                        # and write it out
                        writer.writerow(record)

        # all done
        return


# end of file
