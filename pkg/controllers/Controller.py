# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


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

    # helpers
    def pyre_dump(self):
        """
        Render my state
        """
        # go through my traits
        for trait in self.pyre_configurables():
            # my name
            yield f"{trait.name}: {getattr(self, trait.name)}"

        # all done
        return

    def _autotune(self, **kwds):
        """
        Adjust my parameters based on a sample of the data
        """
        # i don't know much about how to do that
        return

    # constants
    tag = "controller"


# end of file
