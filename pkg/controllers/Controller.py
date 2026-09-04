# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed


# the base controller
class Controller(qed.component, implements=qed.protocols.controller):
    """
    The base class for controller implementations
    """

    # configurable state
    auto = qed.properties.bool(default=True)
    auto.doc = "adjust my parameters by running statistics on a sample of the data"

    # interface
    def autotune(self, stats=None, **kwds):
        """
        Adjust my values based on a sample of my dataset
        """
        # a dataset that arrives without statistics leaves me at my configured values;
        # this happens whenever nobody has measured the product yet, e.g. in a worker
        # that is about to receive the client's controller state anyway
        if stats is None:
            # so there is nothing to tune against
            return
        # if i'm supposed to do it automatically
        if self.auto:
            # process the sample and adjust the parameters
            self._autotune(stats=stats, **kwds)
        # all done
        return

    def widen(self, stats: tuple) -> bool:
        """
        Expand my display bounds to accommodate {stats}, the accumulated whole-dataset
        statistics, without ever touching the user's picks
        """
        # controllers pinned by the user stay exactly where they were put
        if not self.auto:
            # untouched
            return False
        # otherwise, let my flavor decide; it reports whether anything actually moved
        return self._widen(stats=stats)

    def resize(self, *, min: float, max: float) -> bool:
        """
        Set my display bounds to [{min}, {max}] by hand; the new extent must leave my picks in
        place, so the rendered pixels never change, and the edit pins me so that statistics
        can no longer move my bounds
        """
        # an extent that would encroach on my picks is refused
        if not self.accommodates(min=min, max=max):
            # untouched
            return False
        # adopt the bounds
        self.min = min
        self.max = max
        # a hand-set extent is pinned: neither autotune nor widen may move it from now on
        self.auto = False
        # report the move
        return True

    def pin(self) -> None:
        """
        Opt out of automatic adjustments: neither autotune nor widen may move my bounds
        """
        # easy enough
        self.auto = False
        # all done
        return

    def unpin(self, stats: tuple | None = None) -> bool:
        """
        Opt back into automatic adjustments and, if {stats} are on offer, stretch my bounds to
        accommodate them right away, since no further statistics may ever arrive
        """
        # release the pin
        self.auto = True
        # without statistics, there is nothing to catch up on
        if stats is None:
            # so report that the bounds stayed put
            return False
        # otherwise, stretch, and report whether anything moved
        return self.widen(stats=stats)

    def accommodates(self, *, min: float, max: float) -> bool:
        """
        Check whether the extent [{min}, {max}] is well formed and leaves my picks inside it
        """
        # a degenerate or inverted extent is meaningless
        if min >= max:
            # so refuse it
            return False
        # get the span of my picks
        envelope = self._envelope()
        # a controller without picks accommodates any well formed extent
        if envelope is None:
            # so accept it
            return True
        # unpack
        lowest, highest = envelope
        # the extent must enclose the picks
        return min <= lowest and highest <= max

    # metamethods
    def __init__(self, **kwds):
        # chain up
        super().__init__(**kwds)
        # mark me as clean
        self.dirty = False
        # all done
        return

    # framework hooks
    def pyre_traitModified(self, **kwds):
        """
        Hook invoked when one of my traits is modified
        """
        # mark me as dirty
        self.dirty = True
        # all done
        return

    # helpers
    def pyre_dump(self):
        """
        Render my state
        """
        # go through my traits
        for trait in self.pyre_configurables():
            # the trait name and its value
            yield f"{trait.name}: {getattr(self, trait.name)}"
        # all done
        return

    def _autotune(self, **kwds):
        """
        Adjust my parameters based on a sample of the data
        """
        # i don't know much about how to do that
        return

    def _widen(self, stats: tuple) -> bool:
        """
        Expand my display bounds to accommodate {stats}
        """
        # by default, there is nothing to expand
        return False

    def _envelope(self) -> tuple | None:
        """
        Report the span of my picks as a (lowest, highest) pair, or None if i have no picks
        """
        # by default, i have no picks for an extent to accommodate
        return None

    # constants
    tag = "controller"
    # traits that shape the presentation but not the rendered pixels; they are excluded from
    # tile identities, so adjusting them does not invalidate cached work
    cosmetic = ("min", "max")


# end of file
