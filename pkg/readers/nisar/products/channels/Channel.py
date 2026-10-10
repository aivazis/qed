# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from ....Channel import Channel as Base

# the slicer that reads the rasters of products
from ...Fetch import Fetch


# the base of the channels of nisar products
class Channel(Base):
    """
    The base class for the channels of nisar products, whose tiles are read out of a dataset of
    the product, or out of a level of its pyramid
    """

    # constants
    tag = None
    category = None
    # whether my kernel knows how to paint the cells where the raster has nothing to say.
    # the channels that build their own pipeline do; the ones that delegate to the shared
    # {native} kernels do not yet, and asking them would be an argument they cannot take
    absence = False
    # the cells my pipeline reads windows of the rasters into, by the family of my kernel
    cellTypes = {"slc": "complex64", "real": "float32"}
    # the slicer at the head of my recipe, which reads windows of datasets and pyramid levels
    slicerClass = Fetch

    # interface
    def tile(self, source, zoom, origin, shape, datatype, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # ask the dataset which of its sources serve this zoom; a product with decimated
        # levels answers with one of them and a smaller zoom, for the same pixels. the
        # companion rasters a masked render reads come back at the same depth as the data,
        # because the kernel reads all of them with one origin and one stride
        data, companions, residual = source.resolve(zoom=zoom)
        # turn what is left of the zoom into per-axis strides
        stride = tuple(2**level for level in residual)
        # the cells my pipeline reads, if there is one
        cell = self.cellTypes.get(self.category)
        # with the pipeline of my recipe, if i have one, was asked to use it, and read no
        # companions, which no recipe knows about yet
        if (
            self.engine == "flow"
            and cell is not None
            and not companions
            and self.pipeline() is not None
        ):
            # wrap whichever source answered in a raster; it holds no cells, only what the
            # slicer needs to read a window of them, so it is made for every tile
            raster = qed.libqed.nisar.flow.raster(
                source=data, datatype=datatype, cell=cell, name=f"{self.pyre_name}.raster"
            )
            # and render through my pipeline, reading the window at what is left of the zoom
            return self.flow(rasters={"raster": raster}, origin=origin, shape=shape, stride=stride)
        # otherwise, render with the kernel
        return self.iterators(
            source=source,
            data=data,
            companions=companions,
            datatype=datatype,
            origin=origin,
            shape=shape,
            stride=stride,
            **kwds,
        )

    def iterators(self, source, data, companions, datatype, origin, shape, stride, **kwds):
        """
        Render the tile at {origin}+{shape} of {data}, the source of {source} that serves the
        zoom, read with its {companions} at the given {stride}, with the fused kernel of my
        family
        """
        # lookup the pipeline category
        category = getattr(qed.libqed.nisar, self.category)
        # look for the tile maker in {libqed}
        pipeline = getattr(category, self.tag)
        # a kernel that can tell absence from measurement is told what the product declared
        # it writes where it has nothing to say; the declaration belongs to the product, so
        # it is the same answer whichever of its levels supplied the cells
        marking = {"fill": source.fill} if self.absence else {}
        # build the visualization pipeline and return it
        return pipeline(
            source=data,
            datatype=datatype,
            origin=origin,
            shape=shape,
            stride=stride,
            **companions,
            **marking,
            **kwds,
        )


# end of file
