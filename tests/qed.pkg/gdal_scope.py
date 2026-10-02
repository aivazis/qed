#! /usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that a GDAL reader of an object in a bucket keeps the profile and the region its uri names
to the folder of the object: gdal sees them for everything it reads from there, and nothing else
in the process sees them, neither through the environment nor through the folders of other
readers
"""

# externals
import os

# support
import qed

# carefully, since GDAL is optional
try:
    # get the bindings
    from osgeo import gdal
# without them
except ImportError:
    # there is nothing to check
    raise SystemExit(0)


# the environment before any reader gets involved
before = {key: os.environ.get(key) for key in ("AWS_PROFILE", "AWS_REGION")}

# a reader of an object in a bucket, with a profile and a region of its own
reader = qed.readers.native.gdal()(
    name="scope.gdal", uri="s3://someone@us-east-9/some-bucket/some/folder/raster.tif"
)
# build the name gdal knows the object by
name = reader._vsis3(uri=reader.uri)

# it is the object in the bucket
assert name == "/vsis3/some-bucket/some/folder/raster.tif", name
# gdal sees the settings for the object
assert gdal.GetPathSpecificOption(name, "AWS_PROFILE", None) == "someone"
assert gdal.GetPathSpecificOption(name, "AWS_REGION", None) == "us-east-9"
# and for the files next to it, e.g. its overviews
overviews = "/vsis3/some-bucket/some/folder/raster.tif.ovr"
assert gdal.GetPathSpecificOption(overviews, "AWS_PROFILE", None) == "someone"
# but not for anything in another folder
elsewhere = "/vsis3/some-bucket/other/raster.tif"
assert gdal.GetPathSpecificOption(elsewhere, "AWS_PROFILE", None) is None
# and the environment of this process is untouched
assert {key: os.environ.get(key) for key in before} == before

# clean up
gdal.ClearPathSpecificOptions("/vsis3/some-bucket/some/folder")


# end of file
