# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import journal
# support
import qed


# application engine
class Panel(qed.shells.command, family="qed.cli.ux"):
    """
    Select application behavior that is mapped to the capabilities of the web client
    """


    # interface
    def dataset(self, name):
        """
        Get the named dataset
        """
        # look it up and return it
        return self.datasets[name]


    def tile(self, src, data, channel, zoom, origin, shape, **kwds):
        """
        Generate a BMP encoded tile from the supplied specification
        """
        # look up the dataset
        dataset = self.dataset(name=data)
        # get the viz flow associated with the selected {channel}
        viz = dataset.channel(name=channel)
        # render a tile and return it
        return viz.tile(source=dataset, zoom=zoom, origin=origin, shape=shape)


    # metamethods
    def __init__(self, plexus, docroot, **kwds):
        # chain up
        super().__init__(plexus=plexus, **kwds)

        # get the known data sources and build a registry of available data sets
        self.datasets = {
            # map the pyre id to the dataset
            str(data.pyre_id): data
            # for all known readers
            for src in plexus.datasets
            # for all available datasets in each reader
            for data in src.datasets}

        # all done
        return


# end of file
