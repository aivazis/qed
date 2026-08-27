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
    def autotune(self, **kwds):
        """
        Adjust my values based on a sample of my dataset
        """
        # if i'm supposed to do it automatically
        if self.auto:
            # process the sample and asjust the parameters
            self._autotune(**kwds)
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

    # constants
    tag = "controller"
    # traits that shape the presentation but not the rendered pixels; they are excluded from
    # tile identities, so adjusting them does not invalidate cached work
    cosmetic = ("min", "max")


# end of file
