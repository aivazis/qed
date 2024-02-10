# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# parser
def parse(uri):
    """
    Parse the metadata for a data product and return its configuration
    """
    # get the XML parsing support from {pyre}
    import pyre.xml

    # get the XML document factory
    from .Document import Document as document

    # open the document stream
    stream = open(uri, mode="r")
    # make an XML parser
    parser = pyre.xml.newReader()
    # parse and return the result
    return parser.read(stream=stream, document=document())


# end of file
