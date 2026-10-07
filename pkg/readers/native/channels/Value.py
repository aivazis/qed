# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Channel import Channel


# a channel for displaying real values
class Value(Channel, family="qed.channels.native.value"):
    """
    Make a visualization pipeline to display real values
    """

    # configurable state
    range = qed.protocols.controller(default=qed.controllers.linearRange)
    range.doc = "the manager of the range of values to render"

    engine = qed.properties.str()
    engine.default = "iterators"
    engine.validators = qed.constraints.isMember("iterators", "flow")
    engine.doc = "render with the fused iterators, or with a pipeline of flow factories"

    # interface
    def autotune(self, **kwds):
        """
        Use the {stats} gathered on a data sample to adjust the range configuration
        """
        # chain up
        super().autotune(**kwds)
        # notify my range
        self.range.autotune(**kwds)
        # all done
        return

    def controllers(self, **kwds):
        """
        Generate the controllers that manipulate my state
        """
        # chain up
        yield from super().controllers(**kwds)
        # my range
        yield self.range, self.pyre_trait(alias="range")
        # all done
        return

    def eval(self, pixel):
        """
        Get the {pixel} value
        """
        # easy enough
        return pixel

    def project(self, pixel):
        """
        Compute the real part of a {pixel}
        """
        # only one rep
        yield pixel, ""
        # all done
        return

    def tile(self, source, zoom, origin, shape, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # with the iterators
        if self.engine == "iterators":
            # add my configuration and chain up
            return super().tile(
                source=source,
                zoom=zoom,
                origin=origin,
                shape=shape,
                min=self.range.low,
                max=self.range.high,
                **kwds,
            )
        # otherwise, with the flow pipeline, which i make on first use and keep, along with the
        # graphs it builds for each tile shape
        if self._pipeline is None:
            # make it
            self._pipeline = qed.libqed.native.pipelines.Value()
        # turn the zoom levels into per-axis strides
        stride = tuple(2**level for level in zoom)
        # and render
        return self._pipeline.render(
            source=source.data,
            origin=origin,
            shape=shape,
            stride=stride,
            min=self.range.low,
            max=self.range.high,
        )

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the flow pipeline, made on first use
        self._pipeline = None
        # all done
        return

    # constants
    tag = "value"

    # the description of the pipeline
    @classmethod
    def description(cls):
        """
        The flow that describes what i compute
        """
        # a value, painted gray
        return qed.channels.value


# end of file
