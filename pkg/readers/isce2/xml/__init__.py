# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved

# externals
import qed

# document parts
from .Document import Document as document


# high level metadata extractor
def metadata(uri):
    """
    Given the {uri} of a data product, extract the metadata from its auxiliary file
    """
    # build the metadata object
    metadata = qed.readers.metadata()
    # cast and attach the dataset uri
    metadata.uri = uri
    # form the file name; no S3 support here
    data = qed.primitives.path(metadata.uri.address)
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
    parser = qed.xml.newReader()
    # parse and return the result
    return parser.read(stream=stream, document=document(metadata=metadata))


# low level parser of the auxiliary file
def parse(uri):
    """
    Parse the auxiliary of a data product and return the metadata
    """
    # coerce the input into a uri
    uri = qed.primitives.uri.parse(uri)
    # extract its address and turn it into a path
    aux = qed.primitives.path(uri.address)
    # form the product uri
    product = uri.clone()
    # by stripping the trailing suffix from the auxiliary file path
    product.address = aux.withSuffix()

    # build the metadata object
    metadata = qed.readers.metadata()
    # attach the product uri
    metadata.uri = product
    # open the companion file
    stream = open(aux, mode="r")
    # make an XML parser
    parser = qed.xml.newReader()
    # parse and return the result
    return parser.read(stream=stream, document=document(metadata=metadata))


# the set of known dataset suffixes
supported = ["slc", "int", "unw"]


# end of file
