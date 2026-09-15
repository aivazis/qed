# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal
import re


# the metaclass for all NISAR products
class Descriptor(qed.actor):
    """
    The metaclass for NISAR product descriptors
    """

    # initialize a class record
    def __init__(self, name, bases, attributes, **kwds):
        """
        Called when the descriptor class record has been instantiated
        """
        # chain up
        super().__init__(name, bases, attributes, **kwds)
        # if i'm not supposed to touch this record any further
        if self.pyre_internal:
            # bail
            return
        # build the sequence of token recognizers
        recognizers = (
            # look up the recognizers
            self.pyre_trait(name).lexer
            # from the sequence of names in the descriptor
            for name in self.sequencer()
        )
        # assemble and store
        self.regex = re.compile("".join(recognizers))
        # all done
        return

    def __call__(self, granule, name=None, **kwds):
        """
        Parse the {granule} and use it to create an instance of the product descriptor
        """
        # make sure all descriptors have names
        if name is None:
            # by deriving a name from the {granule] id as the {name} when necessary
            name = f"{granule}.descriptor"
        # if we are not supposed to touch this record
        if self.pyre_internal:
            # chain up and move on with the descriptor instantiation
            return super().__call__(name=name, granule=granule, **kwds)

        # parse the granule
        match = self.regex.match(granule)
        # if it didn't match expectations
        if not match:
            # we have a problem
            channel = journal.warning("qed.readers.nisar.daac")
            # complain
            channel.line(f"{self}:")
            channel.line(f"could not recognize '{granule}'")
            channel.line(f"as a product of type '{self.__name__}'")
            # flush
            channel.log()
            # and bail
            return
        # if everything went well, build the construction arguments
        meta = {
            # set the {name} trait to a value extracted from the granule
            # trait.name: match.group(name)
            trait.name: match.group(trait.name)
            # for all names in my sequencer
            for trait in self.pyre_configurables()
            # that are not marked internal
            if not trait.internal
        }
        # construct and hand off the product descriptor
        return super().__call__(name=name, granule=granule, **meta, **kwds)


# end of file
