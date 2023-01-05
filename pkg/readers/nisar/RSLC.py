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

    # public data
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

        # grab my file
        d = self.h5.pyre_id
        # get my tag
        tag = self.tag
        # alias my constants
        DATASET = self.DATASET
        FREQUENCIES = self.FREQUENCIES
        POLARIZATIONS = self.POLARIZATIONS

        for band in self.selectors["band"]:
            # attempt to
            try:
                # get the list of frequencies for this band
                frequencies = d.dataset(FREQUENCIES.format(band=band)).strings()
            # if anything goes wrong
            except Exception:
                # move on
                continue

            # go through them
            for frequency in frequencies:
                # attempt
                try:
                    # form the group name with the list polarizations
                    polGrp = POLARIZATIONS.format(band=band, tag=tag, freq=frequency)
                    # get the list of polarizations
                    polarizations = d.dataset(polGrp).strings()
                # if anything goes wrong
                except Exception:
                    # move on
                    continue
                # go through them
                for polarization in polarizations:
                    # attempt
                    try:
                        # form the name of the dataset
                        dName = DATASET.format(
                            band=band, tag=tag, freq=frequency, pol=polarization
                        )
                        # get the HDF5 dataset
                        data = d.dataset(dName)
                    # if anything goes wrong
                    except Exception:
                        # move on
                        continue
                    # generate a {pyre} name for the dataset
                    name = f"{self.pyre_name}.{band}.{frequency}.{polarization}"
                    # build its selector table
                    selector = {
                        "band": band,
                        "frequency": frequency,
                        "polarization": polarization,
                    }
                    # pack its configuration
                    config = {
                        "uri": self.uri,
                        "shape": data.shape,
                        "selector": selector,
                    }
                    # stop discovery
                    discovery.stop()
                    # and start stats
                    stats.start()
                    # instantiate it
                    slc = SLC(name=name, data=data, **config)
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
    # older NISAR RSLCs are not tagged correctly
    tag = "SLC"

    # layout
    DATASET = "/science/{band}SAR/{tag}/swaths/frequency{freq}/{pol}"
    FREQUENCIES = "/science/{band}SAR/identification/listOfFrequencies"
    POLARIZATIONS = (
        "/science/{band}SAR/{tag}/swaths/frequency{freq}/listOfPolarizations"
    )


# end of file
