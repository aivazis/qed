# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed


# the RSLC reader
class RSLC(qed.readers.h5, family="qed.nisar.readers.rslc"):
    """
    The reader of RSLC files
    """


    # public data
    # my selectors
    selectors = qed.protocols.selectors()
    selectors.doc = "a map of selector names to their allowed values"
    # the full set of allowed values
    selectors.default = {
        "frequency": ["A", "B"],
        "polarization": ["HH", "HV", "VH", "VV"],
    }


    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)

        # grab my file
        d = self.h5

        # get the list of frequencies in this file
        frequencies = d.dataset(self.FREQS).strings()
        # go through them
        for frequency in frequencies:
            # attempt
            try:
                # get the list of polarizations
                polarizations = d.dataset(self.POLS.format(freq=frequency)).strings()
            # if anything goes wrong
            except Exception:
                # move on
                continue
            # go through them
            for polarization in polarizations:
                # attempt
                try:
                    # get the HDF5 dataset
                    data = d.dataset(self.DATASET.format(freq=frequency, pol=polarization))
                # if anything goes wrong
                except Exception:
                    # move on
                    continue
                # wrap it up
                slc = qed.nisar.datasets.slc(uri=self.uri, data=data,
                                             frequency=frequency, polarization=polarization)
                # and add it to my dataset
                self.datasets.append(slc)

        # all done
        return


    # constants
    DATASET = "/science/LSAR/SLC/swaths/frequency{freq}/{pol}"
    FREQS = "/science/LSAR/identification/listOfFrequencies"
    POLS = "/science/LSAR/SLC/swaths/frequency{freq}/listOfPolarizations"


# end of file
