# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import journal

# superclass
from .Node import Node


# the data product
class Image(Node):
    """
    The metadata for a data product
    """

    # the set of children nodes
    elements = "component", "property"

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # my components
        self.components = {}
        # and my properties
        self.properties = {}
        # all done
        return

    # event hooks
    def notify(self, parent, **kwds):
        """
        Attach the product metadata to the document
        """
        # retrieve the object we decorate
        metadata = parent.dom
        # go through the entries in the property map
        for src, dst in self.map.items():
            # and attempt to
            try:
                # unpack the corresponding property
                value = self.properties[src].value
            # if the source isn't there
            except KeyError:
                # no worries, there is a default
                continue
            # if there is something wrong with the content
            except self.CastingError as error:
                # make a channel
                channel = journal.warning("qed.readers.isce2.xml")
                # report
                channel.line(f"{error}")
                channel.line(f"while extracting '{src}' to '{dst}'")
                # flush
                channel.log()
                # and use the default value
                continue
            # if all goes well, store the value
            setattr(metadata, dst, value)
        # all done
        return

    # the property map
    map = {
        "image_type": "product",
        "description": "description",
        "width": "width",
        "length": "height",
        "number_bands": "bands",
        "scheme": "interleaving",
        "data_type": "type",
        "byte_order": "endian",
        "ISCE_VERSION": "version",
    }


# end of file
