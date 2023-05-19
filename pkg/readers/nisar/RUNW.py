# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


# support
import qed

# superclass
from .H5 import H5

# my dataset
from .products.UNW import UNW


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
    }

    # metamethods
    def __init__(self, name, **kwds):
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
                        data = getattr(swath.interferogram, polarization)
                    # if not there
                    except AttributeError:
                        # just ignore it
                        continue
                    # get the dataset
                    dataset = data.unwrappedPhase
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
                    # instantiate it
                    slc = UNW(name=name, data=dataset, **config)
                    # add the dataset to my pile
                    self.datasets.append(slc)
        # all done
        return

    # constants
    tag = "RUNW"


# end of file
