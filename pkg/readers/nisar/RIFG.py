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
from .products.Coherence import Coherence
from .products.Mask import Mask
from .products.Real import Real
from .products.SLC import SLC


# the RIFG reader
class RIFG(H5, family="qed.readers.nisar.rifg"):
    """
    The reader of RIFG files
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
        "layer": ["interferogram", "coherence", "mask"],
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
            rifg = getattr(sar, self.tag)
            # and the group with the swaths
            swaths = rifg.swaths
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
                    channel = journal.warning("qed.nisar.rifg")
                    # and complain
                    channel.line(f"while exploring '{self.pyre_name}'")
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
                        channel = journal.warning("qed.nisar.rifg")
                        # and complain
                        channel.line(f"while exploring '{self.pyre_name}'")
                        channel.line(
                            f"no '{polarization}' polarization in the '{frequency}' swath"
                        )
                        # flush
                        channel.log()
                        # and move on
                        continue

                    # attempt to
                    try:
                        # get the mask from the frequency swath; this is common to all polarizations
                        # but we are reading here so the gui looks ok
                        mask = swath.interferogram.mask
                    # if it's not present
                    except AttributeError:
                        # so grab a channel
                        channel = journal.warning("qed.nisar.runw")
                        # and complain
                        channel.line(f"while exploring '{self.pyre_name}':")
                        channel.indent()
                        channel.line(f"no 'mask' dataset in the 'interferogram' group")
                        channel.line(f"in band '{band}', frequency '{frequency}'")
                        channel.outdent()
                        # flush
                        channel.log()
                    # otherwise
                    else:
                        # generate a name for the dataset
                        name = (
                            f"{self.pyre_name}.{band}.{frequency}.{polarization}.mask"
                        )
                        # build its selector
                        selector = {
                            "band": band,
                            "frequency": frequency,
                            "polarization": polarization,
                            "layer": "mask",
                        }
                        # pack its configuration
                        config = {
                            "uri": self.uri,
                            "shape": mask.shape,
                            "selector": selector,
                        }
                        # instantiate it
                        dataset = Mask(name=name, data=mask, **config)
                        # add the dataset to my pile
                        self.datasets.append(dataset)

                    # attempt to
                    try:
                        # get the interferogram dataset
                        interferogram = data.wrappedInterferogram
                    # if the dataset is not present
                    except AttributeError:
                        # so grab a channel
                        channel = journal.warning("qed.nisar.rifg")
                        # and complain
                        channel.line(f"while exploring '{self.pyre_name}':")
                        channel.indent()
                        channel.line(f"no 'wrappedInterferogram' dataset ")
                        channel.line(
                            f"in band '{band}', frequency '{frequency}, polarization '{polarization}"
                        )
                        channel.outdent()
                        # flush
                        channel.log()
                    # otherwise
                    else:
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
                            "shape": interferogram.shape,
                            "selector": selector,
                        }
                        # instantiate it
                        dataset = SLC(name=name, data=interferogram, **config)
                        # add the dataset to my pile
                        self.datasets.append(dataset)

                    # attempt to
                    try:
                        # get the coherence dataset
                        coherence = data.coherenceMagnitude
                    # if the dataset is not present
                    except AttributeError:
                        # so grab a channel
                        channel = journal.warning("qed.nisar.rifg")
                        # and complain
                        channel.line(f"while exploring '{self.pyre_name}':")
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
                            "shape": coherence.shape,
                            "selector": selector,
                        }
                        # instantiate it
                        dataset = Coherence(
                            name=name, data=coherence, mask=mask, **config
                        )
                        # add the dataset to my pile
                        self.datasets.append(dataset)

        # all done
        return

    # constants
    tag = "RIFG"


# end of file
