# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal

# superclass
from .H5 import H5

# my datasets
from .products.Covariance import Covariance
from .products.GCOVMask import GCOVMask
from .products.SLC import SLC


# the GCOV reader
class GCOV(H5, family="qed.readers.nisar.gcov"):
    """
    The reader of GCOV files
    """

    # user configurable data
    # my selectors
    selectors = qed.protocols.selectors()
    selectors.doc = "a map of selector names to their allowed values"
    # the full set of allowed values
    selectors.default = {
        "band": ["L", "S"],
        "frequency": ["A", "B"],
        "cov": [
            "HHHH",
            "HHHV",
            "HHVH",
            "HHVV",
            "HVHV",
            "HVVH",
            "HVVV",
            "VHVH",
            "VHVV",
            "VVVV",
            "RHRH",
            "RHRV",
            "RVRH",
            "RVRV",
            "mask",
        ],
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
        # and the registered datasets
        registered = self.datasets

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
            gcov = getattr(sar, self.tag)
            # and the group with the grids
            grids = gcov.grids
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
                    channel = journal.warning("qed.nisar.gcov")
                    # and complain
                    channel.line(f"while exploring '{self.pyre_name}'")
                    channel.line(
                        f"no '{frequency}' frequency in the '{band}'-band grids"
                    )
                    # flush
                    channel.log()
                    # and move on
                    continue
                # look up the grid group for this frequency
                grid = getattr(grids, f"frequency{frequency}")

                # a product that turns out to have no mask leaves the datasets it would
                # have applied to without one, rather than with the one from the last
                # frequency we looked at
                companion = None
                # attempt to
                try:
                    # get the mask
                    mask = grid.mask
                # if it is not present
                except AttributeError:
                    # so grab a channel
                    channel = journal.warning("qed.nisar.gcov")
                    # and complain
                    channel.line(f"while exploring '{self.pyre_name}':")
                    channel.indent()
                    channel.line(f"no 'mask' dataset")
                    channel.line(f"in band '{band}', frequency '{frequency}'")
                    channel.outdent()
                    # flush
                    channel.log()
                # otherwise
                else:
                    # generate a name for the dataset
                    name = f"{self.pyre_name}.{band}.{frequency}.mask"
                    # build its selector
                    selector = {
                        "band": band,
                        "frequency": frequency,
                        "cov": "mask",
                    }
                    # pack its configuration
                    config = {
                        "uri": self.uri,
                        "shape": mask.shape,
                        "selector": selector,
                    }
                    # instantiate it; the datasets it applies to are handed the mask
                    # product rather than its payload, so a masked render can ask it
                    # for the decimated level that matches the one the data came from
                    companion = GCOVMask(name=name, data=mask, **config)
                    # add the dataset to my pile
                    registered.append(companion)

                # get the list of polarizations present
                terms = grid.listOfCovarianceTerms
                # go through them
                for term in terms:
                    # some datasets lie, so attempt to
                    try:
                        # get the dataset
                        dataset = getattr(grid, term)
                    # if not there
                    except AttributeError:
                        # so grab a channel
                        channel = journal.warning("qed.nisar.gcov")
                        # and complain
                        channel.line(f"while exploring '{self.pyre_name}'")
                        channel.line(f"no '{term}' in the '{frequency}' grid")
                        # flush
                        channel.log()
                        # and move on
                        continue
                    # generate a name for the dataset
                    name = f"{self.pyre_name}.{band}.{frequency}.{term}"
                    # build its selector
                    selector = {
                        "band": band,
                        "frequency": frequency,
                        "cov": term,
                    }
                    # pack its configuration
                    config = {
                        "uri": self.uri,
                        "shape": dataset.shape,
                        "selector": selector,
                    }
                    # the off-diagonal terms
                    if term[0:2] != term[2:4]:
                        # are complex
                        data = SLC(name=name, data=dataset, **config)
                    # the diagonal terms
                    else:
                        # are real
                        data = Covariance(
                            name=name, data=dataset, mask=companion, **config
                        )
                    # add the dataset to my pile
                    registered.append(data)
        # all done
        return

    # constants
    tag = "GCOV"


# end of file
