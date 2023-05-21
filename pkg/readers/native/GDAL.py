# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved

# support
import qed
import journal
from osgeo import gdal

# dataset
from . import datasets


# a reader that employs gdal to read supported file formats
class GDAL(
    qed.flow.factory, family="qed.readers.native.gdal", implements=qed.protocols.reader
):
    """
    A reader that uses GDAL
    """

    # public data
    uri = qed.properties.uri(scheme="file")
    uri.doc = "the uri of the data source"

    selectors = qed.protocols.selectors()
    selectors.default = {
        "raster": [],
    }
    selectors.doc = "a map of selector names to their allowed values"

    datasets = qed.properties.list(schema=qed.protocols.dataset.output())
    datasets.doc = "the list of data sets provided by the reader"

    # metamethods
    def __init__(self, name, **kwds):
        # chain up
        super().__init__(name=name, **kwds)
        # open the file
        dataset = gdal.Open(str(self.uri.address))
        # if something went wrong
        if dataset is None:
            # make a channel
            channel = journal.error("qed.readers.native.gdal")
            # report
            channel.line(f"'{self.uri}' not found")
            # complain
            channel.log()
            # and bail
            return
        # if all is good with the data source, figure out how many rasters are available
        rasters = dataset.RasterCount
        # get my selector
        bands = []
        # go through them
        for rid in range(rasters):
            # add to the selector
            bands.append(str(rid))
            # make a dataset
            band = datasets.gdal(
                name=f"s{self.pyre_name}.band_{rid:02}", rid=rid, dataset=dataset
            )
            # add it to my pile
            self.datasets.append(band)
        # remember the data product
        self.product = dataset
        # and update th selectors
        self.selectors["raster"] = bands
        # all done
        return


# end of file
