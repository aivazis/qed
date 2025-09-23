# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed
import journal

# superclass
from .H5 import H5

# my dataset
from .products.BFPQSLC import BFPQSLC


# the RRSD reader
class RRSD(H5, family="qed.readers.nisar.rrsd"):
    """
    The reader of RRSD files
    """

    # user configurable data
    # my selectors
    selectors = qed.protocols.selectors()
    selectors.doc = "a map of selector names to their allowed values"
    # the full set of allowed values
    selectors.default = {
        "band": ["L"],
        "frequency": ["A", "B"],
        "polarization": ["HH", "HV", "VH", "VV"],
    }

    # implementation details
    def _loadDatasets(self):
        """
        Discover the available datasets
        """
        # make a timer that measures the layout discovery time
        discovery = qed.timers.wall(f"qed.profiler.discovery.{self.pyre_name}")
        # and another that measures the amount of time it takes to collect statistics
        stats = qed.timers.wall(f"qed.profiler.stats.{self.pyre_name}")
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
            rrsd = getattr(sar, self.tag)
            # and the group with the swaths
            swaths = rrsd.swaths
            # get the list of frequencies for this band
            frequencies = sar.identification.listOfFrequencies
            # go through them
            for frequency in frequencies:
                # attempt to
                try:
                    # look up the swath group for this frequency
                    swath = getattr(swaths, f"frequency{frequency}")
                # sometimes the product lies
                except AttributeError:
                    # so grab a channel
                    channel = journal.warning("qed.nisar.rrsd")
                    # and complain
                    channel.line(f"while exploring '{name}'")
                    channel.line(
                        f"no '{frequency}' frequency in the '{band}'-band swaths"
                    )
                    # flush
                    channel.log()
                    # and move on
                    continue
                # and get the list of transmit polarizations present
                txPolarizations = swath.listOfTxPolarizations
                # go through them
                for txPol in txPolarizations:
                    # open the group
                    tx = getattr(swath, f"tx{txPol}")
                    # and get the list of receive polarizations
                    rxPolarizations = tx.listOfRxPolarizations
                    # go through them
                    for rxPol in rxPolarizations:
                        # assemble the combined polarization marker
                        pol = f"{txPol}{rxPol}"
                        #   open the group
                        rx = getattr(tx, f"rx{rxPol}")
                        # attempt to
                        try:
                            # get the dataset
                            dataset = getattr(rx, f"{pol}")
                        # if not there
                        except AttributeError:
                            # so grab a channel
                            channel = journal.warning("qed.nisar.rrsd")
                            # and complain
                            channel.line(f"while exploring '{name}'")
                            channel.line(
                                f"no '{pol}' dataset in the '{frequency}' swath"
                            )
                            # flush
                            channel.log()
                            # and move on
                            continue
                        # attempt to
                        try:
                            # grab the BFPQ lookup table as well
                            bfpq = getattr(rx, "BFPQLUT")
                        # if not there
                        except AttributeError:
                            # so grab a channel
                            channel = journal.warning("qed.nisar.rrsd")
                            # and complain
                            channel.line(f"while exploring '{name}'")
                            channel.line(
                                f"no BFPQ lookup table for the '{pol}' dataset in the '{frequency}' swath"
                            )
                            # flush
                            channel.log()
                            # and move on
                            continue

                        # load the BFPQ lookup table into memory
                        lut = bfpq.read().data

                        # generate a name for the dataset
                        name = f"{self.pyre_name}.{band}.{frequency}.{pol}"
                        # build its selector
                        selector = {
                            "band": band,
                            "frequency": frequency,
                            "polarization": pol,
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
                        slc = BFPQSLC(name=name, data=dataset, bfpq=lut, **config)
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
    tag = "RRSD"


# end of file
