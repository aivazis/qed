# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import pyre.xml

# nodes
from .Component import Component as component
from .Doc import Doc as doc
from .Module import Module as module
from .Name import Name as name
from .Image import Image as image
from .Property import Property as property
from .Value import Value as value


# the document
class Document(pyre.xml.document):
    """
    Metadata for an ISCE2 data product
    """

    # the elements
    image = pyre.xml.element(tag="imageFile", handler=image, root=True)

    component = pyre.xml.element(tag="component", handler=component)
    doc = pyre.xml.element(tag="doc", handler=doc)
    module = pyre.xml.element(tag="factorymodule", handler=module)
    name = pyre.xml.element(tag="factoryname", handler=name)
    property = pyre.xml.element(tag="property", handler=property)
    value = pyre.xml.element(tag="value", handler=value)

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # initialize my contents
        self.dom = None
        # all done
        return


# end of file
