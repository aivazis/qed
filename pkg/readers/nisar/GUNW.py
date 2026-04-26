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
from .products.Mask import Mask
from .products.Real import Real
from .products.SLC import SLC
from .products.UNW import UNW


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
        "layer": [
            "unwrappedPhase",
            "unwrappedCoherence",
            "unwrappedMask",
            "wrappedInterferogram",
            "wrappedCoherence",
            "wrappedMask",
            "ionosphere",
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
                    channel.line(f"while exploring '{self.pyre_name}'")
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
                    # add the datasets under the {unwrappedInterferogram} group
                    self._registerUnwrappedDatasets(
                        grid=grid,
                        band=band,
                        frequency=frequency,
                        polarization=polarization,
                    )
                    # and the datasets under the {wrappedInterferogram} group
                    self._registerWrappedDatasets(
                        grid=grid,
                        band=band,
                        frequency=frequency,
                        polarization=polarization,
                    )

        # all done
        return

    def _registerUnwrappedDatasets(self, grid, band, frequency, polarization):
        """
        Register the datasets under the {unwrappedInterferogram} group
        """
        # some datasets lie, so attempt to
        try:
            # get the group with the datasets
            data = getattr(grid.unwrappedInterferogram, polarization)
        # if not there
        except AttributeError:
            # so grab a channel
            channel = journal.warning("qed.nisar.gunw")
            # and complain
            channel.line(f"while exploring '{self.pyre_name}'")
            channel.line(
                f"no polarization '{polarization}' in the '{frequency}' interferogram"
            )
            # flush
            channel.log()
            # and bail
            return

        # get the pile of registered datasets
        registered = self.datasets

        # attempt to
        try:
            # get the mask from the frequency swath; this is common to all polarizations
            # but we are reading here so the gui looks ok
            mask = grid.unwrappedInterferogram.mask
        # if it's not present
        except AttributeError:
            # so grab a channel
            channel = journal.warning("qed.nisar.gunw")
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
            name = f"{self.pyre_name}.{band}.{frequency}.{polarization}.unwrappedMask"
            # build its selector
            selector = {
                "band": band,
                "frequency": frequency,
                "polarization": polarization,
                "layer": "unwrappedMask",
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
            registered.append(dataset)

        # attempt to
        try:
            # get the unwrapped phase
            unwrappedPhase = data.unwrappedPhase
        # if the dataset is not available
        except AttributeError:
            # so grab a channel
            channel = journal.warning("qed.nisar.gunw")
            # and complain
            channel.line(f"while exploring '{self.pyre_name}':")
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
                "shape": unwrappedPhase.shape,
                "selector": selector,
            }
            # instantiate it
            dataset = UNW(name=name, data=unwrappedPhase, mask=mask, **config)
            # add the dataset to my pile
            registered.append(dataset)

        # attempt to
        try:
            # read the unwrapped coherence layer
            coherence = data.coherenceMagnitude
        # if the dataset is not available
        except AttributeError:
            # so grab a channel
            channel = journal.warning("qed.nisar.gunw")
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
            name = (
                f"{self.pyre_name}.{band}.{frequency}.{polarization}.coherenceMagnitude"
            )
            # build its selector
            selector = {
                "band": band,
                "frequency": frequency,
                "polarization": polarization,
                "layer": "unwrappedCoherence",
            }
            # pack its configuration
            config = {
                "uri": self.uri,
                "shape": coherence.shape,
                "selector": selector,
            }
            # instantiate it
            dataset = Real(name=name, data=coherence, **config)
            # add the dataset to my pile
            registered.append(dataset)

        # attempt to
        try:
            # get the unwrapped phase
            ionosphere = data.ionospherePhaseScreen
        # if the dataset is not available
        except AttributeError:
            # so grab a channel
            channel = journal.warning("qed.nisar.gunw")
            # and complain
            channel.line(f"while exploring '{self.pyre_name}':")
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
            name = f"{self.pyre_name}.{band}.{frequency}.{polarization}.ionosphere"
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
                "shape": ionosphere.shape,
                "selector": selector,
            }
            # instantiate it
            dataset = UNW(name=name, data=ionosphere, mask=mask, **config)
            # add the dataset to my pile
            registered.append(dataset)

        # all done
        return

    def _registerWrappedDatasets(self, grid, band, frequency, polarization):
        """
        Register the datasets under the {unwrappedInterferogram} group
        """
        # some datasets lie, so attempt to
        try:
            # get the dataset
            wrapped = getattr(grid.wrappedInterferogram, polarization)
        # if not there
        except AttributeError:
            # so grab a channel
            channel = journal.warning("qed.nisar.gunw")
            # and complain
            channel.line(f"while exploring '{self.pyre_name}'")
            channel.line(
                f"no polarization '{polarization}' in the '{frequency}' interferogram"
            )
            # flush
            channel.log()
            # and bail
            return

        # get the pile of registered datasets
        registered = self.datasets

        # attempt to
        try:
            # get the mask from the frequency swath; this is common to all polarizations
            # but we are reading here so the gui looks ok
            mask = grid.wrappedInterferogram.mask
        # if it's not present
        except AttributeError:
            # so grab a channel
            channel = journal.warning("qed.nisar.gunw")
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
            name = f"{self.pyre_name}.{band}.{frequency}.{polarization}.wrappedMask"
            # build its selector
            selector = {
                "band": band,
                "frequency": frequency,
                "polarization": polarization,
                "layer": "wrappedMask",
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
            registered.append(dataset)

        # attempt to
        try:
            # get the wrapped interferogram
            wrappedInterferogram = wrapped.wrappedInterferogram
        # if the dataset is not available
        except AttributeError:
            # so grab a channel
            channel = journal.warning("qed.nisar.gunw")
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
                "layer": "wrappedInterferogram",
            }
            # pack its configuration
            config = {
                "uri": self.uri,
                "shape": wrappedInterferogram.shape,
                "selector": selector,
            }
            # instantiate it
            dataset = SLC(name=name, data=wrappedInterferogram, **config)
            # add the dataset to my pile
            registered.append(dataset)

        # attempt to
        try:
            # read the wrapped coherence layer
            coherence = wrapped.coherenceMagnitude
        # if the dataset is not available
        except AttributeError:
            # so grab a channel
            channel = journal.warning("qed.nisar.gunw")
            # and complain
            channel.line(f"while exploring '{self.pyre_name}':")
            channel.indent()
            channel.line(f"no wrapped 'coherenceMagnitude' dataset ")
            channel.line(
                f"in band '{band}', frequency '{frequency}, polarization '{polarization}"
            )
            channel.outdent()
            # flush
            channel.log()
        # otherwise
        else:
            # generate a name for the dataset
            name = (
                f"{self.pyre_name}.{band}.{frequency}.{polarization}.wrappedCoherence"
            )
            # build its selector
            selector = {
                "band": band,
                "frequency": frequency,
                "polarization": polarization,
                "layer": "wrappedCoherence",
            }
            # pack its configuration
            config = {
                "uri": self.uri,
                "shape": coherence.shape,
                "selector": selector,
            }
            # instantiate it
            dataset = Real(name=name, data=coherence, **config)
            # add the dataset to my pile
            registered.append(dataset)

        # all done
        return

    # constants
    tag = "GUNW"


# end of file
