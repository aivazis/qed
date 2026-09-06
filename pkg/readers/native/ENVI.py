# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import math

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
    in the header. A product with more than one band yields one dataset per band, selectable by
    name, each a plane of the mapping of the whole product wherever the interleave put it.
    """

    # public data
    header = qed.properties.uri(scheme="file")
    header.default = None
    header.doc = "the location of the ENVI header; left unset, it is looked for next to the product"

    # implementation details
    def _loadDatasets(self, cell, shape):
        """
        Build my datasets: one for the product when it holds a single band, and one per band
        otherwise, each a sub-grid of the mapping of the whole product
        """
        # get the header
        hdr = self._header
        # the number of bands, with the ENVI default when the header does not say
        bands = hdr.bands if hdr is not None and hdr.bands is not None else 1
        # a single band is a flat file
        if bands == 1:
            # so the flat reader knows what to do
            return super()._loadDatasets(cell=cell, shape=shape)
        # the layout of the whole product, in interleave order
        layout = hdr.shape
        # the path to the product
        path = qed.primitives.path(self.uri.address)
        # the file must hold the whole product; a short file would let the render machinery read
        # past the end of the mapping
        required = math.prod(layout) * cell.bytes
        # measure it
        actual = path.stat().st_size
        # if it is too small
        if actual < required:
            # make a channel
            channel = journal.error("qed.readers.native.envi")
            # complain
            channel.line(f"'{path}' is too small for the declared layout")
            channel.line(f"{bands} bands of {tuple(shape)} {cell.cell} cells require")
            channel.line(f"{required} bytes, but the file holds only {actual}")
            # flush
            channel.log()
            # and bail
            return
        # lay a grid over the whole product, in the byte order of the file
        cube = qed.libpyre.grid.map(uri=str(path), shape=layout, cell=cell.ordered, create=False)
        # the band axis sits where the interleave put it
        axis = self.axes[hdr.interleave or "bsq"]
        # the bands are known by the names in the header when it names them all, and by their
        # ordinals otherwise
        names = hdr.bandNames
        # check
        if not names or len(names) != bands:
            # fall back to ordinals
            names = [str(band + 1) for band in range(bands)]
        # publish the selector
        self.selectors = {"band": tuple(names)}
        # go through the bands
        for band, name in enumerate(names):
            # the index that picks the plane of this band out of the cube
            index = [slice(None)] * len(layout)
            # by pinning the band axis
            index[axis] = band
            # the plane: a sub-grid that shares the mapping of the whole product
            plane = cube[tuple(index)]
            # build the dataset over it
            dataset = qed.readers.native.datasets.mmap(
                # named by the ordinal of the band, which is stable whatever the header calls it
                name=f"{self.pyre_name}.{band + 1}",
                # the product
                uri=self.uri,
                # the layout of the plane
                shape=shape,
                cell=cell,
                tile=cell.tile,
                # its identity
                selector={"band": name},
                # and its payload
                data=plane,
            )
            # and add it to the pile
            self.datasets.append(dataset)
        # every band is present
        self.available = {"band": set(names)}
        # all done
        return

    def _resolveShape(self):
        """
        Complete my cell and shape from the ENVI header, then fall back on the file for whatever
        is still missing
        """
        # get the header, and keep it for the dataset construction
        hdr = self._header = self._describe()
        # if there is one
        if hdr is not None:
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

    # constants
    # the position of the band axis in the layout of a product, by interleave
    axes = {"bsq": 0, "bil": 1, "bip": 2}

    # private data
    _header = None  # the ENVI header, once read


# end of file
