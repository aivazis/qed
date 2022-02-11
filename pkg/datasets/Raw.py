# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# support
import qed


# raw dataset, i.e. a dataset in binary file with no metadata
class Raw(qed.flow.product, family="qed.datasets.raw", implements=qed.protocols.dataset):
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
    cell.default = None
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


    # public data
    @property
    def data(self):
        """
        Provide access to my data source
        """
        # delegate
        return self.open()


    # interface
    def channel(self, name):
        """
        Get the visualization workflow for the given {channel}
        """
        # look up the channel and return it
        return self.channels[name]


    def open(self):
        """
        Initialize my data source
        """
        # get my data source
        data = self._data

        # if i'm not already attached to a data source
        if data is None:
            # build the name of the buffer factory
            memoryType = f"{self.cell.tag}ConstMap"
            # look up the factory in the {pyre::memory} bindings
            bufferFactory = getattr(qed.libpyre.memory, memoryType)
            # make the memory buffer
            buffer = bufferFactory(str(self.uri))

            # realize the shape
            shape = qed.libpyre.grid.Shape2D(shape=self.shape)
            # build the packing
            packing = qed.libpyre.grid.Canonical2D(shape=shape)
            # grab the grid factory
            gridFactory = getattr(qed.libpyre.grid, f"{memoryType}Grid2D")
            # put it all together
            grid = gridFactory(packing, buffer)

            # attach it
            self._data = grid

        # return the data source
        return data


    def close(self):
        """
        Shutdown my data source
        """
        # deallocate the data buffer
        self._data = None
        # all done
        return


    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # make a placeholder for my data object
        self._data = None
        # all done
        return


# end of file
