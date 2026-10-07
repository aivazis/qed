# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Channel import Channel


# a channel for displaying the amplitude of complex values
class Amplitude(Channel, family="qed.channels.native.amplitude"):
    """
    Make a visualization pipeline to display the amplitude of complex values
    """

    # configurable state
    amplitude = qed.protocols.controller(default=qed.controllers.logRange)
    amplitude.doc = "the manager of the range of values to render"
    amplitude.quantity = "amplitude"

    engine = qed.properties.str()
    engine.default = "iterators"
    engine.validators = qed.constraints.isMember("iterators", "flow")
    engine.doc = "render with the fused iterators, or with a pipeline of flow factories"

    # interface
    def autotune(self, **kwds):
        """
        Use the {stats} gathered on a data sample to adjust the amplitude configuration
        """
        # chain up
        super().autotune(**kwds)
        # notify my amplitude
        self.amplitude.autotune(**kwds)
        # all done
        return

    def controllers(self):
        """
        Generate the controllers that manipulate my state
        """
        # chain up
        yield from super().controllers()
        # my amplitude
        yield self.amplitude, self.pyre_trait(alias="amplitude")
        # all done
        return

    def eval(self, pixel):
        """
        Get the {pixel} value
        """
        # easy enough
        return abs(pixel)

    def project(self, pixel):
        """
        Compute the amplitude of a {pixel}
        """
        # only one choice
        yield abs(pixel), ""
        # and done
        return

    def tile(self, source, zoom, origin, shape, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # get my configuration
        low = 10**self.amplitude.low
        high = 10**self.amplitude.high
        # with the iterators
        if self.engine == "iterators":
            # add my configuration and chain up
            return super().tile(
                source=source, zoom=zoom, origin=origin, shape=shape, min=low, max=high, **kwds
            )
        # otherwise, with the flow pipeline for the cells of the source, which i make on first
        # use and keep, along with the graphs it builds for each tile shape
        cell = source.cell.cell
        # look it up
        pipeline = self._pipelines.get(cell)
        # if this is the first tile of this cell type
        if pipeline is None:
            # make the pipeline
            pipeline = getattr(qed.libqed.native.pipelines, cell).Amplitude()
            # and remember it
            self._pipelines[cell] = pipeline
        # turn the zoom levels into per-axis strides
        stride = tuple(2**level for level in zoom)
        # and render
        return pipeline.render(
            source=source.data, origin=origin, shape=shape, stride=stride, min=low, max=high
        )

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # the flow pipelines, by the cell type of the source, made on first use
        self._pipelines = {}
        # all done
        return

    # constants
    tag = "amplitude"

    # the description of the pipeline
    @classmethod
    def description(cls):
        """
        The flow that describes what i compute
        """
        # the amplitude, painted gray
        return qed.channels.amplitude


# end of file
