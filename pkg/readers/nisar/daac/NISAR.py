# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# metaclass
from .Descriptor import Descriptor

# tokens
from . import tokens


# the base descriptor for all NISAR products
class NISAR(qed.component, metaclass=Descriptor, internal=True):
    """
    The RRST product descriptor
    """

    # literals
    nisar = tokens.nisar()
    separator = tokens.separator()

    # interface
    @property
    def gid(self):
        """
        Reconstruct my granule id from my state
        """
        # collect the values from the tokens in the order they appear in my sequencer
        values = (
            # look up the field value and format it accordingly
            self.pyre_trait(alias=name).gid(descriptor=self)
            # from my sequence of token names
            for name in self.sequencer()
        )
        # assemble and return
        return "".join(values)

    # interface
    def report(self, channel):
        """
        Generate a field report and place it in {channel}
        """
        # show me
        channel.line(f"descriptor: {self}")
        # indent
        channel.indent()
        # what i understood
        channel.line(f"    gid: {self.gid}")
        # the granule that was passed int
        channel.line(f"granule: {self.granule}")
        # mark the section with the fields
        channel.line(f"fields:")
        # indent
        channel.indent()
        # go through my traits
        for trait in self.pyre_configurables():
            # traits that are marked internal
            if trait.internal:
                # get skipped
                continue
            # and chow the value of each
            channel.line(f"{trait.name}: {getattr(self, trait.name)}")
        # outdent
        channel.outdent()
        # outdent
        channel.outdent()
        # all done
        return

    # metamethods
    def __init__(self, name, granule, **kwds):
        # chain up
        super().__init__(name=name, **kwds)
        # record the granule
        self.granule = granule
        # all done
        return

    # implementation details
    @classmethod
    def sequencer(cls):
        """
        Generate the sequence of token names as they appear in valid granule ids of my type
        """
        # the sequence common to all NISAR products
        yield from [
            # the prefix
            "nisar",
            # a separator
            "separator",
        ]
        # all done
        return


# end of file
