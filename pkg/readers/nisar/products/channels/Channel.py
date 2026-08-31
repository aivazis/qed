# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed


# a channel is visualization workflow
class Channel(qed.flow.dynamic, implements=qed.protocols.channel):
    """
    The base class for all channels
    """

    # constants
    tag = None
    category = None
    # whether my kernel knows how to paint the cells where the raster has nothing to say.
    # the channels that build their own pipeline do; the ones that delegate to the shared
    # {native} kernels do not yet, and asking them would be an argument they cannot take
    absence = False

    # interface
    def autotune(self, **kwds):
        """
        Use the {stats} gathered on a data sample to adjust the range configuration
        """
        # nothing to do
        return

    def controllers(self):
        """
        Generate the set of controllers that can manipulate my state
        """
        # by default, nothing
        return []

    def eval(self, pixel):
        """
        Extract the channel value from a {pixel}
        """
        # don't kow what to do
        raise NotImplementedError(f"class {type(self).__name__} must implement 'eval'")

    def project(self, pixel):
        """
        Compute the channel representation of a {pixel}
        """
        # don't kow what to do
        raise NotImplementedError(
            f"class {type(self).__name__} must implement 'project'"
        )

    def tile(self, source, zoom, origin, shape, datatype, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # lookup the pipeline category
        category = getattr(qed.libqed.nisar, self.category)
        # look for the tile maker in {libqed}
        pipeline = getattr(category, self.tag)
        # ask the dataset which of its sources serve this zoom; a product with decimated
        # levels answers with one of them and a smaller zoom, for the same pixels. the
        # companion rasters a masked render reads come back at the same depth as the data,
        # because the kernel reads all of them with one origin and one stride
        data, companions, residual = source.resolve(zoom=zoom)
        # turn what is left of the zoom into per-axis strides
        stride = tuple(2**level for level in residual)
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

    def update(self, **kwds):
        """
        Update the state of one of my controllers
        """
        # nothing for me to do
        return {}


# end of file
