# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# superclass
from .Channel import Channel


# a channel for displaying the mean power of a stack of complex values
class MeanPower(Channel, family="qed.channels.nisar.meanpower"):
    """
    Make a visualization pipeline that displays the mean power, mean(|z|^2), of a stack
    """

    # configurable state
    power = qed.protocols.controller(default=qed.controllers.logRange)
    power.doc = "the manager of the range of powers to render"

    # interface
    def autotune(self, stats, **kwds):
        """
        Use the mean-power {stats} gathered on a sample to adjust the power configuration
        """
        # chain up
        super().autotune(stats=stats, **kwds)
        # my {stats} are already mean-power statistics, so tune my range with them directly
        self.power.autotune(stats=stats, **kwds)
        # all done
        return

    def controllers(self):
        """
        Generate the controllers that manipulate my state
        """
        # chain up
        yield from super().controllers()
        # my power range
        yield self.power, self.pyre_trait(alias="power")
        # all done
        return

    def eval(self, pixel):
        """
        Get the {pixel} value
        """
        # the power of a single sample is its squared magnitude
        return abs(pixel) ** 2

    def project(self, pixel):
        """
        Compute the power representation of a {pixel}
        """
        # only one choice
        yield abs(pixel) ** 2, ""
        # all done
        return

    def tile(self, source, zoom, origin, shape, datatype, members=None, **kwds):
        """
        Render a mean-power tile from the members of a {source} stack

        When {members} is given, it is the subset of member datasets that participate; otherwise
        every member of the {source} does.
        """
        # my pipeline reduces several sources at once
        pipeline = qed.libqed.nisar.stack.meanpower
        # turn the shape into a {pyre::grid::shape_t}
        shape = qed.libpyre.grid.Shape2D(shape=shape)
        # the origin into a {pyre::grid::index_t}
        origin = qed.libpyre.grid.Index2D(index=origin)
        # and the zoom into strides
        stride = qed.libpyre.grid.Index2D(index=tuple(2**level for level in zoom))
        # the participating members default to every member of the source
        participants = source.members if members is None else members
        # collect the data handle of each participating member
        sources = [member.data.dataset for member in participants]
        # lift my range out of log scale
        low = 10 ** self.power.low
        # at both ends
        high = 10 ** self.power.high
        # build the visualization pipeline and return it
        return pipeline(
            sources=sources,
            datatype=datatype,
            origin=origin,
            shape=shape,
            stride=stride,
            min=low,
            max=high,
        )

    # constants
    tag = "meanpower"
    category = "stack"


# end of file
