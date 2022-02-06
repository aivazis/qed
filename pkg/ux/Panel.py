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
    def tile(self, src, data, channel, zoom, origin, shape):
        """
        Generate a BMP encoded tile from the supplied specification
        """
        # encode the tile
        tile = "x".join(map(str, origin)) + "+" + "x".join(map(str, shape))
        # make a channel
        chnl = journal.debug("qed.ux.panel")
        chnl.log(f"{data} {channel} {zoom} {tile}")

        # look up the dataset
        dataset = self.datasets[data]
        # get the data source
        source = dataset.data

        return
        # get the channel selector
        # pick = xxx.channel(source=source, channel=channel)
        # make the bitmap
        # bmp = xxx.viz(pick=pick, shape=shape)

        # and return the bitmap
        # return self.sample


    # metamethods
    def __init__(self, plexus, docroot, **kwds):
        # chain up
        super().__init__(plexus=plexus, **kwds)

        # make a registry of data sources
        readers = {str(src.pyre_id): src for src in plexus.datasets}
        # and one of datasets
        datasets = {str(data.pyre_id): data for src in readers.values() for data in src.datasets}

        # make a channel
        channel = journal.debug("qed.ux.panel")
        # go through the readers
        for ruuid, reader in readers.items():
            # sign on
            channel.line(f"reader: {ruuid}")
            # go through the datasets
            for data in reader.datasets:
                # show me the id
                channel.line(f"    data: {data.pyre_id}")
        # flush
        channel.log()

        # attach them
        self.readers = readers
        self.datasets = datasets

        # initialize the registry of visualization workflows
        self.vizflows =  {}

        # MGA: set up a sample tile to send while debugging
        # self.sample = docroot["graphics/tile.bmp"].open(mode="rb").read()

        # all done
        return


# end of file
