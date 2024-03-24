# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed
import journal

# superclass
from .H5 import H5

# my dataset
from .products.SLC import SLC


# the GSLC reader
class GSLC(H5, family="qed.readers.nisar.gslc"):
    """
    The reader of GSLC files
    """

    # user configurable data
    # my selectors
    selectors = qed.protocols.selectors()
    selectors.doc = "a map of selector names to their allowed values"
    # the full set of allowed values
    selectors.default = {
        "band": ["L", "S"],
        "frequency": ["A", "B"],
        "polarization": ["HH", "HV", "VH", "VV"],
    }

    # implementation details
    def _loadDatasets(self):
        """
        Discover the available datasets
        """
        # make a timer that measures the layout discovery time
        discovery = qed.timers.wall(f"qed.profiler.discovery.{name}")
        # and another that measures the amount of time it takes to collect statistics
        stats = qed.timers.wall(f"qed.profiler.stats.{name}")
        # start the discovery timer
        discovery.start()

        # grab the data product
        product = self.product
        # grab my selectors
        selectors = self.selectors
        # get the science group
        science = product.science
        # go through the possible bands
        for band in selectors["band"]:
            # attempt to
            try:
                # get the band group
                sar = getattr(science, f"{band}SAR")
            # if this band isn't present
            except AttributeError:
                # move on
                continue
            # get the product group
            gslc = getattr(sar, self.tag)
            # and the group with the grids
            grids = gslc.grids
            # get the list of frequencies for this band
            frequencies = sar.identification.listOfFrequencies
            # go through them
            for frequency in frequencies:
                # attempt to
                try:
                    # look up the swath group for this frequency
                    grid = getattr(grids, f"frequency{frequency}")
                # sometimes the product lies
                except AttributeError:
                    # so grab a channel
                    channel = journal.warning("qed.nisar.gslc")
                    # and complain
                    channel.line(f"while exploring '{name}'")
                    channel.line(
                        f"no '{frequency}' frequency in the '{band}'-band grids"
                    )
                    # flush
                    channel.log()
                    # and move on
                    continue
                # and get the list of polarizations present
                polarizations = grid.listOfPolarizations
                # go through them
                for polarization in polarizations:
                    # some datasets lie, so attempt to
                    try:
                        # get the dataset
                        dataset = getattr(grid, polarization)
                    # if not there
                    except AttributeError:
                        # so grab a channel
                        channel = journal.warning("qed.nisar.gslc")
                        # and complain
                        channel.line(f"while exploring '{name}'")
                        channel.line(
                            f"no '{polarization}' polarization in the '{frequency}' grid"
                        )
                        # flush
                        channel.log()
                        # and move on
                        continue
                    # generate a name for the dataset
                    name = f"{self.pyre_name}.{band}.{frequency}.{polarization}"
                    # build its selector
                    selector = {
                        "band": band,
                        "frequency": frequency,
                        "polarization": polarization,
                    }
                    # pack its configuration
                    config = {
                        "uri": self.uri,
                        "shape": dataset.shape,
                        "selector": selector,
                    }
                    # stop discovery
                    discovery.stop()
                    # and start stats
                    stats.start()
                    # instantiate it
                    slc = SLC(name=name, data=dataset, **config)
                    # stop stats
                    stats.stop()
                    # and restart discovery
                    discovery.start()
                    # add the dataset to my pile
                    self.datasets.append(slc)
        # stop the discovery
        discovery.stop()
        # all done
        return

    # constants
    tag = "GSLC"


# end of file
