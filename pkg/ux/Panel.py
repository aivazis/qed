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
        # resolve the reader uuid
        reader = self.readers[src]
        # and the dataset
        dataset = self.datasets[data]

        # make the bitmap
        bmp = None
        # and return it
        return bmp


    # metamethods
    def __init__(self, plexus, **kwds):
        # chain up
        super().__init__(plexus=plexus, **kwds)

        # make a registry of datasources
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

        # all done
        return


# end of file
