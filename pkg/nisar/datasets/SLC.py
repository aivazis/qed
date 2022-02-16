# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed


# a NISAR SLC
class SLC(qed.flow.product, family="qed.nisar.datasets.slc", implements=qed.protocols.dataset):
    """
    A raw dataset
    """


    # public data
    # the source
    uri = qed.properties.path()
    uri.default = None
    uri.doc = "the path to the data source"

    # the data layout
    cell = qed.protocols.datatype()
    cell.default = "complex64"
    cell.doc = "the type of the dataset payload"

    channels = qed.properties.dict(schema=qed.protocols.channel())
    channels.default = {}
    channels.doc = "the table of channels supported by this dataset"

    origin = qed.properties.tuple(schema=qed.properties.int())
    origin.default = 0,0
    origin.doc = "the smallest possible index"

    shape = qed.properties.tuple(schema=qed.properties.int())
    shape.default = None
    shape.doc = "the shape of the dataset"

    selector = qed.properties.kv()
    selector.default = {}
    selector.doc = "a key/value map that identifies the dataset to its reader"

    tile = qed.properties.tuple(schema=qed.properties.int())
    tile.default = 512,512
    tile.doc = "the preferred shape of dataset subsets"


    # interface
    def channel(self, name):
        """
        Get the visualization workflow for the given {channel}
        """
        # look up the channel and return it
        return self.channels[name]


    # metamethods
    def __init__(self, uri, data, frequency, polarization, **kwds):
        # chain up
        super().__init__(**kwds)

        # save the path to my file
        self.uri = uri
        # save the dataset
        self.data = data

        # populate my selector
        self.selector["frequency"] = frequency
        self.selector["polarization"] = polarization

        # set my shape
        self.shape = data.shape

        # go through the default channels of my cell type
        for channel in self.cell.channels:
            # and instantiate a workflow for each one
            self.channels[channel] = channel

        # all done
        return


    # constants
    # hint for the tile maker
    storageClass = "HDF5"


# end of file
