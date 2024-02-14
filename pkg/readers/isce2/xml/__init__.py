# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved

# externals
import pyre
import pyre.xml

# document parts
from .Document import Document as document
from .Metadata import Metadata


# parser
def parse(uri):
    """
    Parse the metadata for a data product and return its configuration
    """
    # build the metadata object
    metadata = Metadata()
    # cast and attach the dataset uri
    metadata.uri = uri
    # form the file name; no S3 support here
    data = pyre.primitives.path(metadata.uri.address)
    # get its size and attach it
    metadata.bytes = data.stat().st_size
    # grab its suffix, and skip the dot
    suffix = data.suffix[1:]
    # if the suffix corresponds to a known product type
    if suffix in supported:
        # use it as the product type guess
        metadata.product = suffix
    # form the auxiliary file name
    aux = data.withName(name=data.name + ".xml")
    # if it doesn't exist
    if not aux.exists():
        # this is as far as we can go
        return metadata
    # otherwise, open the companion file
    stream = open(aux, mode="r")
    # make an XML parser
    parser = pyre.xml.newReader()
    # parse and return the result
    return parser.read(stream=stream, document=document(metadata=metadata))


# the set of known dataset suffixes
supported = ["slc", "int", "unw"]


# end of file
