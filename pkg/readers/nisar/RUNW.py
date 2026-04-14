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
from .products.UNW import UNW
from .products.Real import Real


# the RUNW reader
class RUNW(H5, family="qed.readers.nisar.runw"):
    """
    The reader of RUNW files
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
        "layer": ["unwrappedPhase", "ionosphere", "coherence"],
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
            runw = getattr(sar, self.tag)
            # and the group with the swaths
            swaths = runw.swaths
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
                    channel = journal.warning("qed.nisar.runw")
                    # and complain
                    channel.line(f"while exploring '{product.pyre_name}'")
                    channel.line(
                        f"no '{frequency}' frequency in the '{band}'-band swaths"
                    )
                    # flush
                    channel.log()
                    # and move on
                    continue
                # and get the list of polarizations present
                polarizations = swath.listOfPolarizations
                # go through them
                for polarization in polarizations:
                    # some datasets lie, so attempt to
                    try:
                        # get the dataset
                        data = getattr(swath.interferogram, polarization)
                    # if not there
                    except AttributeError:
                        # so grab a channel
                        channel = journal.warning("qed.nisar.runw")
                        # and complain
                        channel.line(f"while exploring '{product.pyre_name}'")
                        channel.line(
                            f"no '{polarization}' polarization in the '{frequency}' interferograms"
                        )
                        # flush
                        channel.log()
                        # and move on
                        continue

                    # attempt to
                    try:
                        # get the unwrapped dataset
                        dataset = data.unwrappedPhase
                    # if the dataset is not available
                    except AttributeError:
                        # so grab a channel
                        channel = journal.warning("qed.nisar.runw")
                        # and complain
                        channel.line(f"while exploring '{product.pyre_name}':")
                        channel.indent()
                        channel.line(f"no 'unwrappedPhase' dataset ")
                        channel.line(
                            f"in band '{band}', frequency '{frequency}, polarization '{polarization}"
                        )
                        channel.outdent()
                        # flush
                        channel.log()
                    # otherwise
                    else:
                        # generate a name for the dataset
                        name = f"{self.pyre_name}.{band}.{frequency}.{polarization}.unwrappedPhase"
                        # build its selector
                        selector = {
                            "band": band,
                            "frequency": frequency,
                            "polarization": polarization,
                            "layer": "unwrappedPhase",
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

                    # attempt to
                    try:
                        # get the ionosphere dataset
                        dataset = data.ionospherePhaseScreen
                    # if the dataset is not present
                    except AttributeError:
                        # so grab a channel
                        channel = journal.warning("qed.nisar.runw")
                        # and complain
                        channel.line(f"while exploring '{product.pyre_name}':")
                        channel.indent()
                        channel.line(f"no 'ionospherePhaseScreen' dataset ")
                        channel.line(
                            f"in band '{band}', frequency '{frequency}, polarization '{polarization}"
                        )
                        channel.outdent()
                        # flush
                        channel.log()
                    # otherwise
                    else:
                        # generate a name for the dataset
                        name = f"{self.pyre_name}.{band}.{frequency}.{polarization}.ionospherePhaseScreen"
                        # build its selector
                        selector = {
                            "band": band,
                            "frequency": frequency,
                            "polarization": polarization,
                            "layer": "ionosphere",
                        }
                        # pack its configuration
                        config = {
                            "uri": self.uri,
                            "shape": dataset.shape,
                            "selector": selector,
                        }
                        # instantiate it
                        iono = UNW(name=name, data=dataset, **config)
                        # add the dataset to my pile
                        self.datasets.append(iono)

                    # attempt to
                    try:
                        # get the coherence dataset
                        dataset = data.coherenceMagnitude
                    # if the dataset is not present
                    except AttributeError:
                        # so grab a channel
                        channel = journal.warning("qed.nisar.runw")
                        # and complain
                        channel.line(f"while exploring '{product.pyre_name}':")
                        channel.indent()
                        channel.line(f"no 'coherenceMagnitude' dataset ")
                        channel.line(
                            f"in band '{band}', frequency '{frequency}, polarization '{polarization}"
                        )
                        channel.outdent()
                        # flush
                        channel.log()
                    # otherwise
                    else:
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
        # all done
        return

    # constants
    tag = "RUNW"


# end of file
