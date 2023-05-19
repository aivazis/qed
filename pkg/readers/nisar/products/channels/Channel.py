# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2023 all rights reserved


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
        raise NotImplementedError(f"class {type(self).__name__} must implement 'rep'")

    def project(self, pixel):
        """
        Compute the channel representation of a {pixel}
        """
        # don't kow what to do
        raise NotImplementedError(f"class {type(self).__name__} must implement 'rep'")

    def tile(self, source, zoom, origin, shape, datatype, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # lookup the pipeline category
        category = getattr(qed.libqed.nisar, self.category)
        # look for the tile maker in {libqed}
        pipeline = getattr(category, self.tag)
        # turn the shape into a {pyre::grid::shape_t}
        shape = qed.libpyre.grid.Shape2D(shape=shape)
        # and the origin into a {pyre::grid::index_t}
        origin = qed.libpyre.grid.Index2D(index=origin)
        return pipeline(
            source=source.data.dataset,
            datatype=datatype,
            zoom=zoom,
            origin=origin,
            shape=shape,
            **kwds,
        )

    def update(self, **kwds):
        """
        Update the state of one of my controllers
        """
        # nothing for me to do
        return {}


# end of file
