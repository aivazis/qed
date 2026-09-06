# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import pyre
import qed
import journal

# superclass
from .Flat import Flat


# a reader of flat binary files described by an ENVI header
class ENVI(Flat, family="qed.readers.native.envi"):
    """
    A reader of flat binary files that come with an ENVI header

    The header supplies what the flat reader would otherwise have to be told: the cell type, the
    byte order of the product, and its shape. A value the user pins explicitly wins over the one
    in the header.
    """

    # public data
    header = qed.properties.uri(scheme="file")
    header.default = None
    header.doc = "the location of the ENVI header; left unset, it is looked for next to the product"

    # implementation details
    def _resolveShape(self):
        """
        Complete my cell and shape from the ENVI header, then fall back on the file for whatever
        is still missing
        """
        # get the header
        hdr = self._describe()
        # if there is one
        if hdr is not None:
            # a product with more than one band needs a band axis the flat dataset does not have
            if hdr.bands is not None and hdr.bands != 1:
                # make a channel
                channel = journal.error("qed.readers.native.envi")
                # complain
                channel.line(f"could not load a dataset from '{self.uri.address}'")
                channel.line(f"the header declares {hdr.bands} bands")
                channel.line(f"multi-band products are not supported yet")
                # flush
                channel.log()
                # and bail
                return
            # a product with an embedded header needs a mapping with an offset, which the flat
            # dataset does not have
            if hdr.offset:
                # make a channel
                channel = journal.error("qed.readers.native.envi")
                # complain
                channel.line(f"could not load a dataset from '{self.uri.address}'")
                channel.line(f"the header declares an offset of {hdr.offset} bytes")
                channel.line(f"products with embedded headers are not supported yet")
                # flush
                channel.log()
                # and bail
                return
            # if the user did not pin a cell type
            if not self.cell:
                # the header supplies it, with the byte order of the product
                self.cell = self._cell(hdr=hdr)
            # get the current value of my shape
            shape = list(self.shape) if self.shape else [0, 0]
            # fill in whatever the user left out from the header
            if not shape[0] and hdr.lines:
                # the height
                shape[0] = hdr.lines
            if not shape[1] and hdr.samples:
                # the width
                shape[1] = hdr.samples
            # if the shape is now fully resolved
            if shape[0] and shape[1]:
                # set it
                self.shape = tuple(shape)
        # chain up for the cell check and the size based fallback
        super()._resolveShape()
        # all done
        return

    def _cell(self, hdr):
        """
        Build the specification of my cell type from the header: its data type, led by the byte
        order marker the datatype protocol understands
        """
        # the native name of the cell
        name = hdr.datatype
        # if the header does not say
        if name is None:
            # make a channel
            channel = journal.error("qed.readers.native.envi")
            # complain
            channel.line(f"could not load a dataset from '{self.uri.address}'")
            channel.line(f"the header does not declare a data type")
            # flush
            channel.log()
            # and bail
            return None
        # the byte order of the product: 0 is little endian, 1 is big endian; the datatype
        # protocol reads the marker and decides whether the host has to swap
        order = hdr.byteOrder
        # without one, the product is taken to be in the host's order
        if order is None:
            # so the bare name will do
            return name
        # otherwise, lead with the marker
        return ("<" if order == 0 else ">") + name

    def _describe(self):
        """
        Read the ENVI header, from where the user said or from next to the product
        """
        # the path to the product
        product = qed.primitives.path(self.uri.address)
        # if the user pointed me to the header
        if self.header is not None:
            # that is the only place to look
            candidates = [qed.primitives.path(self.header.address)]
        # otherwise
        else:
            # ENVI writers put the header next to the product, either with its suffix replaced by
            # {.hdr} or with {.hdr} appended to the full name
            candidates = [
                product.withSuffix(suffix=".hdr"),
                product.parent / (product.name + ".hdr"),
            ]
        # go through them
        for candidate in candidates:
            # skip the ones that do not exist
            if not candidate.exists():
                # and keep looking
                continue
            # carefully
            try:
                # read the header
                return pyre.envi.reader().read(uri=candidate, name=f"{self.pyre_name}.header")
            # if it is not a well formed header
            except pyre.envi.exceptions.ENVIError as error:
                # make a channel
                channel = journal.error("qed.readers.native.envi")
                # complain
                channel.line(f"could not load a dataset from '{self.uri.address}'")
                channel.line(f"while reading its header '{candidate}'")
                channel.line(f"{error}")
                # flush
                channel.log()
                # and bail
                return None
        # none of the candidates exists; make a channel
        channel = journal.error("qed.readers.native.envi")
        # complain
        channel.line(f"could not load a dataset from '{self.uri.address}'")
        channel.line(f"no ENVI header; looked for")
        channel.indent()
        # list the places
        for candidate in candidates:
            # one per line
            channel.line(f"{candidate}")
        channel.outdent()
        channel.line(f"please use '--header' to point to the header")
        # flush
        channel.log()
        # and bail
        return None


# end of file
