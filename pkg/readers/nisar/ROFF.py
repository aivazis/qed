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
from .products.OFF import OFF


# the ROFF reader
class ROFF(H5):
    """
    The reader of ROFF files
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
        "layer": ["1", "2", "3"],
        "axis": ["alongTrack", "slantRange"],
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
            roff = getattr(sar, self.tag)
            # and the group with the swaths
            swaths = roff.swaths
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
                    channel = journal.warning("qed.nisar.roff")
                    # and complain
                    channel.line(f"while exploring '{name}'")
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
                    # carefully, because some data product lie
                    try:
                        # get the group
                        offsets = getattr(swath.pixelOffsets, polarization)
                        # if this polarization dataset doesn't exist
                    except AttributeError:
                        # so grab a channel
                        channel = journal.warning("qed.nisar.roff")
                        # and complain
                        channel.line(f"while exploring '{name}'")
                        channel.line(
                            f"no '{polarization}' polarization in the '{frequency}' pixel offsets"
                        )
                        # flush
                        channel.log()
                        # and move on
                        continue
                    # there is a number of layers
                    for layerName in selectors["layer"]:
                        # get the layer
                        layer = getattr(offsets, f"layer{layerName}")
                        # extract the directional offsets
                        for axis in selectors["axis"]:
                            # get the dataset
                            dataset = getattr(layer, f"{axis}Offset")
                            # generate a name for the dataset
                            name = (
                                f"{self.pyre_name}.{band}.{frequency}."
                                f"{polarization}.layer{layerName}.{axis}"
                            )
                            # build its selector
                            selector = {
                                "band": band,
                                "frequency": frequency,
                                "polarization": polarization,
                                "layer": layerName,
                                "axis": axis,
                            }
                            # pack its configuration
                            config = {
                                "uri": self.uri,
                                "shape": dataset.shape,
                                "selector": selector,
                            }
                            # instantiate it
                            off = OFF(name=name, data=dataset, **config)
                            # add the dataset to my pile
                            self.datasets.append(off)
        # all done
        return

    # constants
    tag = "ROFF"


# end of file
