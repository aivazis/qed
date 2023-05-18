# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# support
import qed

# superclass
from .H5 import H5

# my dataset
from .slc.SLC import SLC


# the RSLC reader
class RSLC(H5, family="qed.readers.nisar.rslc"):
    """
    The reader of RSLC files
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

    # metamethods
    def __init__(self, name, **kwds):
        # make a timer that measures the layout discovery time
        discovery = qed.timers.wall(f"qed.profiler.discovery.{name}")
        # and another that measures the amount of time it takes to collect statistics
        stats = qed.timers.wall(f"qed.profiler.stats.{name}")

        # start the discovery timer
        discovery.start()
        # chain up
        super().__init__(name=name, **kwds)

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
            slc = getattr(sar, self.tag)
            # and the group with the swaths
            swaths = slc.swaths
            # get the list of frequencies for this band
            frequencies = sar.identification.listOfFrequencies
            # go through them
            for frequency in frequencies:
                # look up the swath group for this frequency
                swath = getattr(swaths, f"frequency{frequency}")
                # and get the list of polarizations present
                polarizations = swath.listOfPolarizations
                # go through them
                for polarization in polarizations:
                    # some datasets lie, so attempt to
                    try:
                        # get the dataset
                        dataset = getattr(swath, polarization)
                    # if not there
                    except AttributeError:
                        # just ignore it
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
    tag = "RSLC"


# end of file
