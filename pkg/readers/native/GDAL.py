# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved

# support
import os
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
        dataset = self._open()
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
        # and update the selectors
        self.selectors["raster"] = bands
        # all done
        return

    # implementation details
    def _open(self):
        """
        Retrieve the dataset from my {uri}
        """
        # get my {uri}
        uri = self.uri
        # local files
        if uri.scheme == "file":
            # are easy
            return gdal.Open(str(uri.address))
        # s3 buckets
        if uri.scheme == "s3":
            # extract the profile and region
            region, _, profile, _ = uri.server
            # the uri specifies a profile
            if profile:
                # override the value in the the environment
                os.environ["AWS_PROFILE"] = profile
            # if the uri specifies a region
            if region:
                # override the value in the the environment
                os.environ["AWS_REGION"] = region
            # get the address, expected to be of the form {/bucket/path-to-file}
            address = uri.address
            # assemble the filename
            name = f"/vsis3{address}"
            # make a channel
            channel = journal.info("qed.readers.native.gdal")
            # show me
            channel.line(f"uri: {uri}")
            channel.line(f"   opening: {name}")
            # flush
            channel.log()
            # get the dataset and return it
            return gdal.Open(name)
        # anything else is unsupported
        channel = journal.error("qed.readers.native")
        # so complain
        channel.line(f"unsupported scheme '{uri.scheme}'")
        channel.line(f"in the uri '{uri}")
        channel.line(f"while attempting to read a GDAL dataset")
        channel.line(f"using {self}")
        # flush
        channel.log()
        # and bail, just in case errors aren't fatal
        return


# end of file
