# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal

# superclass
from .H5 import H5

# my dataset
from .products.SLC import SLC
from .products.UNW import UNW
from .products.Real import Real


# the GUNW reader
class GUNW(H5, family="qed.readers.nisar.gunw"):
    """
    The reader of GUNW files
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
	"layer": ["phase","ionosphere","coherence","interferogram","wrapped coherence"],

    }

    # implementation details
    def _loadDatasets(self):
        """
        Discover the available datasets
        """
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
            gunw = getattr(sar, self.tag)
            # and the group with the grids
            grids = gunw.grids
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
                    channel = journal.warning("qed.nisar.gunw")
                    # and complain
                    channel.line(f"while exploring '{name}'")
                    channel.line(
                        f"no frequency '{frequency}' in the band '{band}' grids"
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
                        data = getattr(grid.unwrappedInterferogram, polarization)
                        datawrap = getattr(grid.wrappedInterferogram, polarization)
                    # if not there
                    except AttributeError:
                        # so grab a channel
                        channel = journal.warning("qed.nisar.gunw")
                        # and complain
                        channel.line(f"while exploring '{name}'")
                        channel.line(
                            f"no polarization '{polarization}' in the '{frequency}' interferogram"
                        )
                        # flush
                        channel.log()
                        # and move on
                        continue
                    # get the unwrapped dataset
                    dataset = data.unwrappedPhase
                    # generate a name for the dataset
                    name = f"{self.pyre_name}.{band}.{frequency}.{polarization}.unwrappedPhase"
                    # build its selector
                    selector = {
                        "band": band,
                        "frequency": frequency,
                        "polarization": polarization,
			"layer": "phase",
                    }
                    # pack its configuration
                    config = {
                        "uri": self.uri,
                        "shape": dataset.shape,
                        "selector": selector,
                    }
                    # instantiate it
                    unw = UNW(name=name, data=dataset, **config)
                    # add the dataset to my pile
                    self.datasets.append(unw)
		    # read the unwrapped coherence layer
                    # get the dataset
                    dataset = data.coherenceMagnitude
                    # generate a name for the dataset
                    name = f"{self.pyre_name}.{band}.{frequency}.{polarization}.coherenceMagnitude"
                    # build its selector
                    selector = {
                        "band": band,
                        "frequency": frequency,
                        "polarization": polarization,
			"layer": "coherence",
                    }
                    # pack its configuration
                    config = {
                        "uri": self.uri,
                        "shape": dataset.shape,
                        "selector": selector,
                    }
                    # instantiate it
                    coh = Real(name=name, data=dataset, **config)
                    # add the dataset to my pile
                    self.datasets.append(coh)

                    # get the unwrapped dataset
                    dataset = datawrap.wrappedInterferogram
                    # generate a name for the dataset
                    name = f"{self.pyre_name}.{band}.{frequency}.{polarization}.wrappedInterferogram"
                    # build its selector
                    selector = {
                        "band": band,
                        "frequency": frequency,
                        "polarization": polarization,
			"layer": "interferogram",
                    }
                    # pack its configuration
                    config = {
                        "uri": self.uri,
                        "shape": dataset.shape,
                        "selector": selector,
                    }
                    # instantiate it
                    wrp = SLC(name=name, data=dataset, **config)
                    # add the dataset to my pile
                    self.datasets.append(wrp)
		    # read the unwrapped coherence layer


                    # get the wrapped dataset
                    dataset = datawrap.coherenceMagnitude
                    # generate a name for the dataset
                    name = f"{self.pyre_name}.{band}.{frequency}.{polarization}.wrappedcoherenceMagnitude"
                    # build its selector
                    selector = {
                        "band": band,
                        "frequency": frequency,
                        "polarization": polarization,
			"layer": "wrapped coherence",
                    }
                    # pack its configuration
                    config = {
                        "uri": self.uri,
                        "shape": dataset.shape,
                        "selector": selector,
                    }
                    # instantiate it
                    wcoh = Real(name=name, data=dataset, **config)
                    # add the dataset to my pile
                    self.datasets.append(wcoh)

        # all done
        return

    # constants
    tag = "GUNW"


# end of file
