# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Channel import Channel


# a channel for displaying the temporal coherence of a stack of complex values
class StackCoherence(Channel, family="qed.channels.nisar.stack.coherence"):
    """
    Make a visualization pipeline that displays the coherence, |Σz|/Σ|z|, of a stack
    """

    # configurable state
    range = qed.protocols.controller(default=qed.controllers.linearRange)
    range.doc = "the manager of the range of coherence values to render"

    # interface
    def autotune(self, stats, **kwds):
        """
        Pin the rendering range; coherence is inherently in [0,1], independent of the data
        """
        # chain up
        super().autotune(stats=stats, **kwds)
        # coherence does not depend on the data sample; it always lives in [0,1]
        self.range.updateRange(low=0.0, high=1.0)
        # so fix the controller bounds there too
        self.range.min = 0.0
        self.range.max = 1.0
        # all done
        return

    def controllers(self):
        """
        Generate the controllers that manipulate my state
        """
        # chain up
        yield from super().controllers()
        # my coherence range
        yield self.range, self.pyre_trait(alias="range")
        # all done
        return

    def eval(self, pixel):
        """
        Get the {pixel} value
        """
        # the coherence of a single sample with itself is total
        return 1.0

    def project(self, pixel):
        """
        Compute the coherence representation of a {pixel}
        """
        # only one choice
        yield 1.0, ""
        # all done
        return

    def tile(self, source, zoom, origin, shape, datatype, **kwds):
        """
        Render a coherence tile from the members of a {source} stack
        """
        # my pipeline reduces several sources at once
        pipeline = qed.libqed.nisar.stack.coherence
        # turn the shape into a {pyre::grid::shape_t}
        shape = qed.libpyre.grid.Shape2D(shape=shape)
        # the origin into a {pyre::grid::index_t}
        origin = qed.libpyre.grid.Index2D(index=origin)
        # and the zoom into strides
        stride = qed.libpyre.grid.Index2D(index=tuple(2**level for level in zoom))
        # collect the data handle of each stack member
        sources = [member.data.dataset for member in source.members]
        # build the visualization pipeline and return it; the coherence range is already linear
        return pipeline(
            sources=sources,
            datatype=datatype,
            origin=origin,
            shape=shape,
            stride=stride,
            min=self.range.low,
            max=self.range.high,
        )

    # constants
    tag = "coherence"
    category = "stack"


# end of file
