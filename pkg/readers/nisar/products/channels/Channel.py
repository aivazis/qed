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
        # a render that reads a companion raster alongside the data -- a mask -- reads both
        # with one origin and one stride, so the two must be at the same resolution. the
        # companions have no decimated levels of their own yet, so a render that carries
        # one stays on the product: taking the data from a level while the mask came from
        # the product would pair every cell with the wrong mask value
        if "mask" in kwds:
            # read both at full resolution, the way this always worked
            data, residual = source.data.dataset, tuple(zoom)
        # otherwise ask the dataset which of its sources serves this zoom; a product with
        # decimated levels answers with one of them and a smaller zoom, same pixels
        else:
            # let it choose
            data, residual = source.resolve(zoom=zoom)
        # turn what is left of the zoom into per-axis strides
        stride = tuple(2**level for level in residual)
        # build the visualization pipeline and return it
        return pipeline(
            source=data,
            datatype=datatype,
            origin=origin,
            shape=shape,
            stride=stride,
            **kwds,
        )

    def update(self, **kwds):
        """
        Update the state of one of my controllers
        """
        # nothing for me to do
        return {}


# end of file
