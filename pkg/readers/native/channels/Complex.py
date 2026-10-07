# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Channel import Channel


# a channel for displaying complex values
class Complex(Channel, family="qed.channels.native.complex"):
    """
    Make a visualization pipeline to display complex values
    """

    # configurable state
    amplitude = qed.protocols.controller(default=qed.controllers.logRange)
    amplitude.doc = "the manager of the amplitude of values to render"
    amplitude.quantity = "amplitude"

    phase = qed.protocols.controller(default=qed.controllers.linearRange)
    phase.doc = "the manager of the range of values to render"
    phase.quantity = "phase"

    saturation = qed.protocols.controller(default=qed.controllers.value)
    saturation.doc = "the saturation"
    saturation.quantity = "saturation"

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
        self.amplitude.autotune(**kwds)
        # if i'm supposed
        if self.phase.auto:
            # adjust my phase
            self.phase.min = 0
            self.phase.low = 0
            self.phase.max = 1
            self.phase.high = 1
        # if i'm supposed
        if self.saturation.auto:
            # adjust my saturation
            self.saturation.value = 1
        # all done
        return

    def controllers(self, **kwds):
        """
        Generate the controllers that manipulate my state
        """
        # chain up
        yield from super().controllers(**kwds)
        # my range
        yield self.amplitude, self.pyre_trait(alias="amplitude")
        # my phase
        yield self.phase, self.pyre_trait(alias="phase")
        # and my saturation
        yield self.saturation, self.pyre_trait(alias="saturation")
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
        Represent a {pixel} as a complex number
        """
        # only one rep
        yield pixel, ""
        # all done
        return

    def tile(self, source, zoom, origin, shape, **kwds):
        """
        Generate a tile of the given characteristics
        """
        # unpack my configuration
        low = 10**self.amplitude.low
        high = 10**self.amplitude.high
        lowPhase = self.phase.low
        highPhase = self.phase.high
        saturation = self.saturation.value
        # with the iterators
        if self.engine == "iterators":
            # add my configuration and chain up
            return super().tile(
                source=source,
                zoom=zoom,
                origin=origin,
                shape=shape,
                min=low,
                max=high,
                minPhase=lowPhase,
                maxPhase=highPhase,
                saturation=saturation,
                **kwds,
            )
        # otherwise, with the flow pipeline for the cells of the source, which i make on first
        # use and keep, along with the graphs it builds for each tile shape
        cell = source.cell.cell
        # look it up
        pipeline = self._pipelines.get(cell)
        # if this is the first tile of this cell type
        if pipeline is None:
            # make the pipeline
            pipeline = getattr(qed.libqed.native.pipelines, cell).Complex()
            # and remember it
            self._pipelines[cell] = pipeline
        # turn the zoom levels into per-axis strides
        stride = tuple(2**level for level in zoom)
        # and render
        return pipeline.render(
            source=source.data,
            origin=origin,
            shape=shape,
            stride=stride,
            min=low,
            max=high,
            minPhase=lowPhase,
            maxPhase=highPhase,
            saturation=saturation,
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
    tag = "complex"


# end of file
